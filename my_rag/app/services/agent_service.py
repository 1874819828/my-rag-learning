"""
LangChain Agent 服务（简化版）
"""
from typing import Dict, Any, List
from app.services.agent_tools import get_agent_tools
from app.services.llm_service import llm_service
import re

class SimpleAgent:
    """简化的 Agent 实现"""
    
    def __init__(self):
        """初始化 Agent"""
        self.tools = {tool.name: tool.func for tool in get_agent_tools()}
        self.tool_descriptions = {
            tool.name: tool.description 
            for tool in get_agent_tools()
        }
    
    def _parse_action(self, text: str) -> tuple:
        """
        解析 LLM 输出的 Action
        
        Returns:
            (tool_name, tool_input)
        """
        # 查找 Action 和 Action Input
        action_match = re.search(r'Action:\s*(.+?)(?:\n|$)', text)
        input_match = re.search(r'Action Input:\s*(.+?)(?:\n|$)', text)
        
        if action_match and input_match:
            tool_name = action_match.group(1).strip()
            tool_input = input_match.group(1).strip()
            return tool_name, tool_input
        
        return None, None
    
    def run(self, question: str, max_iterations: int = 3) -> Dict[str, Any]:
        """
        运行 Agent
        
        Args:
            question: 用户问题
            max_iterations: 最大迭代次数
        
        Returns:
            执行结果
        """
        intermediate_steps = []
        
        # 构建工具描述
        tools_desc = "\n".join([
            f"- {name}: {desc}" 
            for name, desc in self.tool_descriptions.items()
        ])
        
        # 初始提示词
        prompt = f"""你是一个智能助手，可以使用工具来回答问题。

可用工具：
{tools_desc}

请按以下格式回答：

Question: {question}
Thought: 我需要思考如何回答这个问题
Action: 工具名称
Action Input: 工具输入
Observation: 工具返回结果
... (可以重复多次)
Thought: 我现在知道答案了
Final Answer: 最终答案

重要：
1. 如果需要查找文档，使用"搜索知识库"
2. 如果需要计算，使用"计算器"
3. 如果需要时间，使用时间工具
4. 如果不需要工具，直接给出 Final Answer

开始！

Question: {question}
Thought:"""
        
        try:
            for iteration in range(max_iterations):
                # 调用 LLM
                response = llm_service.chat(prompt, temperature=0.1)
                print(f"\n[迭代 {iteration + 1}] LLM 响应:\n{response}\n")
                
                # 检查是否有 Final Answer
                if "Final Answer:" in response:
                    final_answer = response.split("Final Answer:")[-1].strip()
                    return {
                        "success": True,
                        "answer": final_answer,
                        "intermediate_steps": intermediate_steps,
                        "tool_calls": len(intermediate_steps)
                    }
                
                # 解析 Action
                tool_name, tool_input = self._parse_action(response)
                
                if tool_name and tool_name in self.tools:
                    # 执行工具
                    print(f"🔧 执行工具: {tool_name}({tool_input})")
                    observation = self.tools[tool_name](tool_input)
                    print(f"📊 工具结果: {observation}")
                    
                    intermediate_steps.append({
                        "tool": tool_name,
                        "input": tool_input,
                        "output": observation
                    })
                    
                    # 更新提示词
                    prompt += f""" {response}
Observation: {observation}
Thought:"""
                else:
                    # 没有找到有效的 Action，直接返回响应
                    return {
                        "success": True,
                        "answer": response,
                        "intermediate_steps": intermediate_steps,
                        "tool_calls": len(intermediate_steps)
                    }
            
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
