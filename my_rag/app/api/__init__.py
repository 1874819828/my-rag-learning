"""
API路由模块
"""
from fastapi import APIRouter
from app.api import chat, upload, conversation, cache, agent

router = APIRouter()

# 注册子路由
router.include_router(chat.router, prefix="/chat", tags=["问答"])
router.include_router(upload.router, prefix="/upload", tags=["文档上传"])
router.include_router(conversation.router, prefix="/conversation", tags=["会话管理"])
router.include_router(cache.router, prefix="/cache", tags=["缓存管理"])
router.include_router(agent.router, prefix="/agent", tags=["智能Agent"])

