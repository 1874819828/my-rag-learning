"""
Milvus向量数据库服务
"""
import warnings
warnings.filterwarnings('ignore')
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient
from app.config import settings

class MilvusService:
    """Milvus向量数据库服务封装"""
    
    def __init__(self):
        self.client = MilvusClient(f"tcp://{settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
        self.collection_name = settings.MILVUS_COLLECTION_NAME
        self.vector_dim = settings.VECTOR_DIM
        self.top_k = settings.TOP_K
        
        # 初始化向量模型（延迟加载，避免服务启动时加载）
        self._embedding_model = None
    
    @property
    def embedding_model(self):
        """延迟加载向量模型"""
        if self._embedding_model is None:
            self._embedding_model = SentenceTransformer(
                'BAAI/bge-small-zh-v1.5',
                device='cpu',
                trust_remote_code=True
            )
        return self._embedding_model
    
    def force_align_dim(self, vec: List[float], target_dim: int = None) -> List[float]:
        """
        强制对齐向量维度
        
        Args:
            vec: 原始向量
            target_dim: 目标维度，默认使用配置的维度
        
        Returns:
            对齐后的向量
        """
        if target_dim is None:
            target_dim = self.vector_dim
        
        if len(vec) > target_dim:
            return vec[:target_dim]  # 裁剪
        elif len(vec) < target_dim:
            return vec + [0.0] * (target_dim - len(vec))  # 补齐
        else:
            return vec
    
    def get_embedding(self, text: str) -> List[float]:
        """
        生成文本向量
        
        Args:
            text: 输入文本
        
        Returns:
            向量列表
        """
        vec = self.embedding_model.encode(text, normalize_embeddings=True).tolist()
        return self.force_align_dim(vec)
    
    def create_collection_if_not_exists(self):
        """创建集合（如果不存在）"""
        if not self.client.has_collection(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=self.vector_dim,
                auto_id=True,
                vector_field_name="vector"
            )
            print(f"✅ 创建Milvus集合：{self.collection_name}")
    
    def drop_collection(self):
        """删除集合"""
        if self.client.has_collection(self.collection_name):
            self.client.drop_collection(self.collection_name)
            print(f"✅ 删除Milvus集合：{self.collection_name}")
    
    def insert_chunks(self, chunks: List[str], metadatas: Optional[List[dict]] = None):
        """
        插入文本块到Milvus
        
        Args:
            chunks: 文本块列表
            metadatas: 可选的元数据列表（如文档ID等）
        """
        self.create_collection_if_not_exists()
        
        data = []
        for idx, chunk in enumerate(chunks):
            vec = self.get_embedding(chunk)
            item = {"content": chunk, "vector": vec}
            if metadatas and idx < len(metadatas):
                item.update(metadatas[idx])
            data.append(item)
        
        self.client.insert(
            collection_name=self.collection_name,
            data=data
        )
        print(f"✅ 成功插入 {len(chunks)} 条数据到Milvus")
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[dict]:
        """
        相似度检索
        
        Args:
            query: 查询文本
            top_k: 返回top k个结果，默认使用配置值
        
        Returns:
            检索结果列表，每个结果包含content和distance
        """
        if top_k is None:
            top_k = self.top_k
        
        query_vec = self.get_embedding(query)
        
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                data=[query_vec],
                limit=top_k,
                search_params={"metric_type": "COSINE"},
                output_fields=["content"]
            )
            
            # 格式化结果 - MilvusClient返回格式：results[0]是第一个查询的结果列表
            hits = []
            if results and len(results) > 0 and len(results[0]) > 0:
                for hit in results[0]:
                    # MilvusClient返回的格式：hit是字典，包含"id", "distance", "entity"等
                    entity = hit.get("entity", {})
                    hits.append({
                        "content": entity.get("content", ""),
                        "distance": hit.get("distance", 0.0)
                    })
            
            return hits
        except Exception as e:
            print(f"Milvus搜索错误: {str(e)}")
            return []
    
    def search_context(self, query: str, top_k: Optional[int] = None) -> str:
        """
        检索并返回拼接的上下文文本
        
        Args:
            query: 查询文本
            top_k: 返回top k个结果
        
        Returns:
            拼接后的上下文文本
        """
        results = self.search(query, top_k)
        if not results:
            return "无相关内容"
        
        context = "\n\n".join([hit["content"] for hit in results])
        return context

# 创建全局实例
milvus_service = MilvusService()

