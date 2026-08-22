"""
Agent 工具定义（原生 Function Calling 版本）

每个工具提供 OpenAI 兼容的 JSON Schema 参数定义，
由 LLM API 的 tools 参数下发，模型通过 tool_calls 结构化返回调用意图。
"""
from typing import Callable, Dict, Any, Optional, Union
from app.services.hybrid_search_service import hybrid_search_service
from app.services.milvus_service import milvus_service
import datetime
import json
import math

class Tool:
    """工具类：函数 + JSON Schema 定义"""

    def __init__(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.func = func
        self.description = description
        self.parameters = parameters or {"type": "object", "properties": {}, "required": []}

    def to_openai_schema(self) -> Dict[str, Any]:
        """转换为 OpenAI 兼容的 tools 参数格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    def execute(self, arguments: Union[str, dict]) -> str:
        """
        执行工具调用

        Args:
            arguments: 模型返回的工具参数（JSON 字符串或已解析的 dict）

        Returns:
            工具执行结果（字符串，作为 tool 消息返回给模型）
        """
        try:
            if isinstance(arguments, str):
                args = json.loads(arguments) if arguments.strip() else {}
            else:
                args = arguments or {}
            if not isinstance(args, dict):
                return f"参数格式错误: 期望 JSON 对象，实际为 {type(args).__name__}"
            return self.func(**args)
        except json.JSONDecodeError:
            return f"参数 JSON 解析失败: {arguments}"
        except TypeError as e:
            return f"参数不匹配: {str(e)}"
        except Exception as e:
            return f"工具执行失败: {str(e)}"

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
        if not milvus_service.enabled:
            return "Milvus 未连接，无法统计文档数量"

        stats = milvus_service.client.get_collection_stats(
            milvus_service.collection_name
        )

        count = stats.get('row_count', 0)
        return f"知识库中共有 {count} 条文档片段"
    except Exception as e:
        return f"统计失败: {str(e)}"

# 定义工具列表
def get_agent_tools():
    """
    获取 Agent 可用的工具列表

    Returns:
        工具列表（每个工具带 JSON Schema 参数定义）
    """
    tools = [
        Tool(
            name="search_knowledge_base",
            func=search_documents,
            description="在知识库中搜索相关文档。适用于回答需要查找文档、资料的问题。",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询文本"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="calculator",
            func=calculator,
            description="计算数学表达式。支持基本运算和常用数学函数（sqrt、abs、round、min、max、pow、pi、e）。",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 '2 + 3 * 4'"
                    }
                },
                "required": ["expression"]
            }
        ),
        Tool(
            name="get_current_time",
            func=get_current_time,
            description="获取当前的日期和时间。不需要输入参数。"
        ),
        Tool(
            name="get_current_date",
            func=get_current_date,
            description="获取今天的日期和星期几。不需要输入参数。"
        ),
        Tool(
            name="count_documents",
            func=count_documents,
            description="统计知识库中的文档片段数量。不需要输入参数。"
        ),
    ]

    return tools
