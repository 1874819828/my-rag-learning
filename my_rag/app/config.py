"""
配置文件
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "root123")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "rag_db")
    
    # Milvus配置
    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT: int = int(os.getenv("MILVUS_PORT", "19530"))
    MILVUS_COLLECTION_NAME: str = "doc_rag_collection"
    VECTOR_DIM: int = 384  # BGE-small-zh-v1.5维度
    TOP_K: int = 3
    
    # Elasticsearch 配置
    ES_HOST: str = os.getenv("ES_HOST", "localhost")
    ES_PORT: int = int(os.getenv("ES_PORT", "9200"))
    ES_INDEX_NAME: str = "rag_documents"
    ES_ENABLED: bool = os.getenv("ES_ENABLED", "true").lower() == "true"
    
    # 混合检索配置
    HYBRID_SEARCH_ENABLED: bool = os.getenv("HYBRID_SEARCH_ENABLED", "true").lower() == "true"
    VECTOR_WEIGHT: float = float(os.getenv("VECTOR_WEIGHT", "0.6"))
    KEYWORD_WEIGHT: float = float(os.getenv("KEYWORD_WEIGHT", "0.4"))

    # Rerank 精排配置（方案1+2+3）
    RERANK_ENABLED: bool = os.getenv("RERANK_ENABLED", "true").lower() == "true"
    RERANK_MODEL: str = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")
    RECALL_TOP_K: int = int(os.getenv("RECALL_TOP_K", "30"))  # 召回阶段扩量（方案2）
    RERANK_TOP_K: int = int(os.getenv("RERANK_TOP_K", "5"))  # rerank 后最终返回数上限
    RERANK_SCORE_THRESHOLD: float = float(os.getenv("RERANK_SCORE_THRESHOLD", "0.3"))  # rerank 概率阈值（方案3）
    VECTOR_DISTANCE_THRESHOLD: float = float(os.getenv("VECTOR_DISTANCE_THRESHOLD", "0.5"))  # 纯向量 COSINE 阈值（无 rerank 时用）
    
    # 智谱AI配置
    ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "")  # 必须从 .env 注入，禁止硬编码
    ZHIPU_API_URL: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    ZHIPU_MODEL: str = "glm-4"
    
    # Redis 配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 缓存过期时间（秒）
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"

settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

