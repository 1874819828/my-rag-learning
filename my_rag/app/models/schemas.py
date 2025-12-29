"""
Pydantic数据模型（用于API请求和响应）
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ===================== 问答相关 =====================
class ChatRequest(BaseModel):
    """问答请求"""
    question: str = Field(..., description="用户问题")
    session_id: Optional[str] = Field(None, description="会话ID，不提供则创建新会话")

class ChatResponse(BaseModel):
    """问答响应"""
    answer: str = Field(..., description="AI回答")
    session_id: str = Field(..., description="会话ID")
    message_id: int = Field(..., description="消息ID")

# ===================== 文档上传相关 =====================
class UploadResponse(BaseModel):
    """文档上传响应"""
    document_id: int = Field(..., description="文档ID")
    filename: str = Field(..., description="文件名")
    status: str = Field(..., description="处理状态")

# ===================== 会话相关 =====================
class ConversationResponse(BaseModel):
    """会话信息"""
    id: int
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    """消息信息"""
    id: int
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationDetailResponse(BaseModel):
    """会话详情（包含消息列表）"""
    id: int
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]
    
    class Config:
        from_attributes = True

# ===================== 文档相关 =====================
class DocumentResponse(BaseModel):
    """文档信息"""
    id: int
    filename: str
    file_path: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

