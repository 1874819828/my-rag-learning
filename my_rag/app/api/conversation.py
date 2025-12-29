"""
会话管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.schemas import (
    ConversationResponse,
    ConversationDetailResponse
)
from app.models.database import Conversation
from app.services.conversation_service import conversation_service

router = APIRouter()

@router.get("/list", response_model=List[ConversationResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取会话列表
    """
    conversations = db.query(Conversation).order_by(
        Conversation.updated_at.desc()
    ).offset(skip).limit(limit).all()
    
    return conversations

@router.get("/{session_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    获取会话详情（包含消息列表）
    """
    detail = conversation_service.get_conversation_detail(db, session_id)
    if not detail:
        raise HTTPException(status_code=404, detail="会话不存在")
    return detail

@router.delete("/{session_id}")
async def delete_conversation(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    删除会话（级联删除所有消息）
    """
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "会话已删除"}

