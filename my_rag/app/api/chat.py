"""
问答API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm_service import llm_service
from app.services.hybrid_search_service import hybrid_search_service
from app.services.conversation_service import conversation_service
from app.services.cache_service import cache_service
from app.config import settings

router = APIRouter()

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    问答接口：接收用户问题，检索相关文档，调用LLM生成回答
    
    流程：
    1. 检查缓存
    2. 如果缓存命中，直接返回
    3. 如果缓存未命中，使用混合检索获取上下文
    4. 调用 LLM 生成回答
    5. 将结果写入缓存
    """
    try:
        # 1. 获取或创建会话
        conversation = conversation_service.get_or_create_session(
            db, request.session_id
        )
        
        # 2. 保存用户问题
        user_message = conversation_service.add_message(
            db, conversation.id, "user", request.question
        )
        
        # 3. 使用混合检索获取上下文
        context = hybrid_search_service.search_context(
            request.question,
            top_k=settings.TOP_K,
            use_hybrid=settings.HYBRID_SEARCH_ENABLED
        )
        
        # 4. 检查缓存
        cached_answer = cache_service.get_cached_answer(request.question, context)
        
        if cached_answer:
            # 缓存命中，直接返回
            answer = cached_answer
            print("🚀 使用缓存答案")
        else:
            # 缓存未命中，调用 LLM 生成回答
            answer = llm_service.chat_with_context(request.question, context)
            
            # 将答案写入缓存
            cache_service.set_cached_answer(
                question=request.question,
                answer=answer,
                context=context
            )
            print("💾 答案已缓存")
        
        # 5. 保存AI回答
        assistant_message = conversation_service.add_message(
            db, conversation.id, "assistant", answer
        )
        
        return ChatResponse(
            answer=answer,
            session_id=conversation.session_id,
            message_id=assistant_message.id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答处理失败: {str(e)}")

