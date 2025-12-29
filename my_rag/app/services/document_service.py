"""
文档处理服务（加载、切分、向量化）
"""
import os
from typing import List
from pathlib import Path
import PyPDF2
from app.services.milvus_service import milvus_service
from app.config import settings
from app.models.database import Document
from sqlalchemy.orm import Session

class DocumentService:
    """文档处理服务"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def split_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """
        切分文本为块
        
        Args:
            text: 原始文本
            chunk_size: 每块的目标字符数
        
        Returns:
            文本块列表
        """
        # 简单按段落切分
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def load_pdf(self, file_path: str) -> str:
        """
        加载PDF文件内容
        
        Args:
            file_path: PDF文件路径
        
        Returns:
            提取的文本内容
        """
        text = ""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"PDF读取失败: {str(e)}")
        
        return text
    
    def load_txt(self, file_path: str) -> str:
        """
        加载TXT文件内容
        
        Args:
            file_path: TXT文件路径
        
        Returns:
            文件文本内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"TXT读取失败: {str(e)}")
    
    def process_and_index(self, file_path: str, document_id: int, db: Session):
        """
        处理文档并索引到 Milvus 和 Elasticsearch
        
        Args:
            file_path: 文件路径
            document_id: 文档ID
            db: 数据库会话
        """
        # 更新文档状态为处理中
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = "processing"
            db.commit()
        
        try:
            # 根据文件类型加载内容
            file_ext = Path(file_path).suffix.lower()
            if file_ext == '.pdf':
                content = self.load_pdf(file_path)
            elif file_ext in ['.txt', '.md']:
                content = self.load_txt(file_path)
            else:
                raise Exception(f"不支持的文件类型: {file_ext}")
            
            # 切分文本
            chunks = self.split_text(content)
            
            # 1. 插入到 Milvus（向量检索）
            metadatas = [{"document_id": document_id} for _ in chunks]
            milvus_service.insert_chunks(chunks, metadatas)
            
            # 2. 插入到 Elasticsearch（关键词检索）
            from app.services.elasticsearch_service import es_service
            if es_service.enabled:
                es_count = es_service.index_documents_bulk(chunks, document_id)
                print(f"✅ ES 索引完成: {es_count} 条")
            
            # 更新文档状态和块数量
            if doc:
                doc.chunk_count = len(chunks)
                doc.status = "completed"
                db.commit()
            
            return len(chunks)
        
        except Exception as e:
            # 更新文档状态为失败
            if doc:
                doc.status = "failed"
                db.commit()
            raise Exception(f"文档处理失败: {str(e)}")

# 创建全局实例
document_service = DocumentService()

