"""
数据库模型（SQLAlchemy ORM）
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Conversation(Base):
    """会话表"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(100), unique=True, index=True, comment="会话ID")
    title = Column(String(200), comment="会话标题（第一条消息的摘要）")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系：一个会话包含多条消息
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """消息表（问答记录）"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), comment="会话ID")
    role = Column(String(20), comment="角色：user/assistant")
    content = Column(Text, comment="消息内容")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关系：消息属于一个会话
    conversation = relationship("Conversation", back_populates="messages")

class Document(Base):
    """文档元信息表"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), comment="文件名")
    file_path = Column(String(500), comment="文件存储路径")
    file_type = Column(String(50), comment="文件类型（pdf/txt/docx等）")
    file_size = Column(Integer, comment="文件大小（字节）")
    chunk_count = Column(Integer, default=0, comment="文档切分后的块数量")
    status = Column(String(20), default="pending", comment="状态：pending/processing/completed/failed")
    created_at = Column(DateTime, server_default=func.now(), comment="上传时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

