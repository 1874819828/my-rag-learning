"""
FastAPI主入口文件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router
from app.database import engine, Base
# 导入所有模型以确保表被创建
from app.models import database  # noqa: F401

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RAG问答系统",
    description="基于Milvus和智谱AI的检索增强生成系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api", tags=["API"])

@app.get("/")
async def root():
    return {"message": "RAG问答系统API", "docs": "/docs"}

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "RAG问答系统",
        "version": "1.0.0"
    }

