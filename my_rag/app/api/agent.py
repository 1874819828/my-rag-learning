"""
Agent API 路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from app.services.agent_service import agent_service

router = APIRouter()

class AgentRequest(BaseModel):
    """Agent 请求"""
    question: str

class AgentResponse(BaseModel):
    """Agent 响应"""
    success: bool
    answer: str
    tool_calls: int = 0
    intermediate_steps: List[Any] = []

@router.post("/chat", response_model=AgentResponse)
async def agent_chat(request: AgentRequest):
    """
    Agent 问答接口
    
    Agent 会自动选择合适的工具来回答问题：
    - 需要查找文档时，使用"搜索知识库"工具
    - 需要计算时，使用"计算器"工具
    - 需要时间信息时，使用时间工具
    """
    try:
        result = agent_service.run(request.question)
        
        return AgentResponse(
            success=result.get("success", False),
            answer=result.get("answer", ""),
            tool_calls=result.get("tool_calls", 0),
            intermediate_steps=result.get("intermediate_steps", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 执行失败: {str(e)}")

@router.get("/tools")
async def get_tools() -> Dict[str, Any]:
    """
    获取 Agent 可用的工具列表
    """
    try:
        tools = agent_service.get_available_tools()
        return {
            "success": True,
            "tools": tools,
            "count": len(tools)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工具列表失败: {str(e)}")

@router.get("/health")
async def agent_health() -> Dict[str, Any]:
    """
    检查 Agent 服务健康状态
    """
    return {
        "status": "healthy",
        "tools_count": len(agent_service.tools)
    }
