"""
会话管理服务
"""
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.database import Conversation, Message
from app.models.schemas import ConversationDetailResponse, MessageResponse

class ConversationService:
    """会话管理服务"""
    
    def create_session(self, db: Session, title: Optional[str] = None) -> Conversation:
        """
        创建新会话
        
        Args:
            db: 数据库会话
            title: 会话标题
        
        Returns:
            会话对象
        """
        session_id = str(uuid.uuid4())
        conversation = Conversation(
            session_id=session_id,
            title=title or "新对话"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation
    
    def get_or_create_session(self, db: Session, session_id: Optional[str] = None) -> Conversation:
        """
        获取或创建会话
        
        Args:
            db: 数据库会话
            session_id: 会话ID，如果不存在则创建新会话
        
        Returns:
            会话对象
        """
        if session_id:
            conversation = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()
            if conversation:
                return conversation
        
        return self.create_session(db)
    
    def add_message(
        self,
        db: Session,
        conversation_id: int,
        role: str,
        content: str
    ) -> Message:
        """
        添加消息到会话
        
        Args:
            db: 数据库会话
            conversation_id: 会话ID
            role: 角色（user/assistant）
            content: 消息内容
        
        Returns:
            消息对象
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # 如果是第一条消息，更新会话标题
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if conversation and conversation.title == "新对话":
            # 使用问题前30个字符作为标题
            if role == "user":
                conversation.title = content[:30] + ("..." if len(content) > 30 else "")
                db.commit()
        
        return message
    
    def get_conversation_detail(self, db: Session, session_id: str) -> Optional[ConversationDetailResponse]:
        """
        获取会话详情（包含消息列表）
        
        Args:
            db: 数据库会话
            session_id: 会话ID
        
        Returns:
            会话详情
        """
        conversation = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if not conversation:
            return None
        
        messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at.asc()).all()
        
        return ConversationDetailResponse(
            id=conversation.id,
            session_id=conversation.session_id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[
                MessageResponse(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at
                )
                for msg in messages
            ]
        )

# 创建全局实例
conversation_service = ConversationService()

