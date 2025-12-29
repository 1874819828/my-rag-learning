"""
文档上传API路由
"""
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import UploadResponse
from app.models.database import Document
from app.services.document_service import document_service
from app.config import settings
from datetime import datetime

router = APIRouter()

@router.post("", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传文档接口：接收文件，保存到本地，记录元信息到MySQL，异步处理并索引到Milvus
    """
    try:
        # 1. 验证文件大小
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制（最大{settings.MAX_FILE_SIZE / 1024 / 1024}MB）"
            )
        
        # 2. 验证文件类型
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.txt', '.pdf', '.md']:
            raise HTTPException(
                status_code=400,
                detail="不支持的文件类型，仅支持 .txt, .pdf, .md"
            )
        
        # 3. 保存文件到本地
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一文件名（时间戳 + 原文件名）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = upload_dir / safe_filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # 4. 记录文档元信息到MySQL
        document = Document(
            filename=file.filename,
            file_path=str(file_path),
            file_type=file_ext[1:],  # 去掉点号
            file_size=len(file_content),
            status="pending"
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # 5. 异步处理文档（切分、向量化、索引到Milvus）
        try:
            chunk_count = document_service.process_and_index(
                str(file_path), document.id, db
            )
            return UploadResponse(
                document_id=document.id,
                filename=file.filename,
                status="completed"
            )
        except Exception as e:
            # 处理失败，但文档记录已保存
            return UploadResponse(
                document_id=document.id,
                filename=file.filename,
                status="failed"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档上传失败: {str(e)}")

