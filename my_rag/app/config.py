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
    
    # 智谱AI配置
    ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "e757e07a420f4e169649a11e0ab51c5c.fm7u0gWQk3ugic2E")
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

