"""
LangChain Agent 工具定义
"""
from typing import Callable
from app.services.hybrid_search_service import hybrid_search_service
from app.services.milvus_service import milvus_service
import datetime
import math

class Tool:
    """简单的工具类"""
    def __init__(self, name: str, func: Callable, description: str):
        self.name = name
        self.func = func
        self.description = description

def search_documents(query: str) -> str:
    """
    搜索知识库文档
    
    Args:
        query: 搜索查询
    
    Returns:
        搜索结果
    """
    try:
        context = hybrid_search_service.search_context(
            query,
            top_k=3,
            use_hybrid=True
        )
        
        if context and context != "无相关内容":
            return f"找到相关文档：\n{context}"
        else:
            return "未找到相关文档"
    except Exception as e:
        return f"搜索失败: {str(e)}"

def calculator(expression: str) -> str:
    """
    计算数学表达式
    
    Args:
        expression: 数学表达式，如 "2 + 3 * 4"
    
    Returns:
        计算结果
    """
    try:
        # 安全的数学表达式计算
        allowed_names = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'pow': pow,
            'sqrt': math.sqrt,
            'pi': math.pi,
            'e': math.e,
        }
        
        # 移除危险字符
        expression = expression.replace('__', '').replace('import', '')
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

def get_current_time() -> str:
    """
    获取当前时间
    
    Returns:
        当前时间字符串
    """
    now = datetime.datetime.now()
    return f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"

def get_current_date() -> str:
    """
    获取当前日期
    
    Returns:
        当前日期字符串
    """
    today = datetime.date.today()
    weekday = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][today.weekday()]
    return f"今天是 {today.strftime('%Y年%m月%d日')} {weekday}"

def count_documents() -> str:
    """
    统计知识库文档数量
    
    Returns:
        文档统计信息
    """
    try:
        stats = milvus_service.es_client.get_collection_stats(
            milvus_service.collection_name
        ) if milvus_service.enabled else {}
        
        count = stats.get('row_count', 0)
        return f"知识库中共有 {count} 条文档片段"
    except Exception as e:
        return f"统计失败: {str(e)}"

# 定义工具列表
def get_agent_tools():
    """
    获取 Agent 可用的工具列表
    
    Returns:
        工具列表
    """
    tools = [
        Tool(
            name="搜索知识库",
            func=search_documents,
            description="在知识库中搜索相关文档。输入：搜索查询文本。适用于回答需要查找文档的问题。"
        ),
        Tool(
            name="计算器",
            func=calculator,
            description="计算数学表达式。输入：数学表达式（如 '2 + 3 * 4'）。支持基本运算和常用数学函数。"
        ),
        Tool(
            name="获取当前时间",
            func=get_current_time,
            description="获取当前的日期和时间。不需要输入参数。"
        ),
        Tool(
            name="获取当前日期",
            func=get_current_date,
            description="获取今天的日期和星期几。不需要输入参数。"
        ),
        Tool(
            name="统计文档数量",
            func=count_documents,
            description="统计知识库中的文档数量。不需要输入参数。"
        ),
    ]
    
    return tools
