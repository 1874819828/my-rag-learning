"""
Agent 服务（原生 Function Calling 版本）

通过 LLM API 的 tools 参数下发工具定义，
模型以结构化 tool_calls 返回调用意图，无需文本协议解析。
"""
from typing import Dict, Any, List
from app.services.agent_tools import get_agent_tools
from app.services.llm_service import llm_service

SYSTEM_PROMPT = """你是一个智能助手，可以调用工具来回答问题。

规则：
1. 回答知识库相关问题时，先调用搜索工具查找文档
2. 需要计算时，调用计算器工具
3. 需要时间或日期信息时，调用对应的时间工具
4. 不需要工具时，直接回答
5. 基于工具返回的结果作答，不要编造内容"""

class SimpleAgent:
    """基于原生 Function Calling 的 Agent 实现"""

    def __init__(self):
        """初始化 Agent"""
        self.tool_list = get_agent_tools()
        self.tools = {tool.name: tool for tool in self.tool_list}
        self.tools_schema = [tool.to_openai_schema() for tool in self.tool_list]

    def _execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        执行模型返回的工具调用，生成 tool 角色消息

        Args:
            tool_calls: 模型返回的 tool_calls 列表

        Returns:
            tool 角色消息列表（与 tool_calls 一一对应）
        """
        tool_messages = []
        for call in tool_calls:
            function_call = call.get("function", {})
            tool_name = function_call.get("name", "")
            arguments = function_call.get("arguments", "{}")

            print(f"🔧 执行工具: {tool_name}({arguments})")

            tool = self.tools.get(tool_name)
            if tool is None:
                observation = f"未知工具: {tool_name}，可用工具: {', '.join(self.tools.keys())}"
            else:
                observation = tool.execute(arguments)

            print(f"📊 工具结果: {observation}")

            tool_messages.append({
                "role": "tool",
                "tool_call_id": call.get("id", ""),
                "content": observation
            })

        return tool_messages

    def run(self, question: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        运行 Agent

        Args:
            question: 用户问题
            max_iterations: 最大迭代次数

        Returns:
            执行结果
        """
        intermediate_steps = []

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]

        try:
            for iteration in range(max_iterations):
                # 调用 LLM（携带工具定义）
                message = llm_service.chat_with_tools(messages, self.tools_schema)
                print(f"\n[迭代 {iteration + 1}] LLM 响应:\n{message}\n")

                tool_calls = message.get("tool_calls") or []

                if not tool_calls:
                    # 模型不再调用工具，返回最终回答
                    return {
                        "success": True,
                        "answer": message.get("content", "").strip(),
                        "intermediate_steps": intermediate_steps,
                        "tool_calls": len(intermediate_steps)
                    }

                # 记录 assistant 的工具调用意图（原样回传，保持 id 对应关系）
                messages.append({
                    "role": "assistant",
                    "content": message.get("content") or "",
                    "tool_calls": tool_calls
                })

                # 执行所有工具调用并追加 tool 消息
                for call, tool_message in zip(tool_calls, self._execute_tool_calls(tool_calls)):
                    function_call = call.get("function", {})
                    intermediate_steps.append({
                        "tool": function_call.get("name", ""),
                        "arguments": function_call.get("arguments", "{}"),
                        "output": tool_message["content"]
                    })
                    messages.append(tool_message)

            # 达到最大迭代次数
            return {
                "success": False,
                "answer": "达到最大迭代次数，无法完成任务",
                "intermediate_steps": intermediate_steps,
                "tool_calls": len(intermediate_steps)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": f"Agent 执行失败: {str(e)}",
                "intermediate_steps": intermediate_steps,
                "tool_calls": len(intermediate_steps)
            }

class AgentService:
    """Agent 服务"""

    def __init__(self):
        """初始化"""
        self.agent = SimpleAgent()
        self.tools = get_agent_tools()

    def run(self, question: str) -> Dict[str, Any]:
        """运行 Agent"""
        return self.agent.run(question)

    def get_available_tools(self) -> List[Dict[str, str]]:
        """获取可用工具列表"""
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self.tools
        ]

# 创建全局实例
agent_service = AgentService()
