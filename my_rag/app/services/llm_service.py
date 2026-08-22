"""
LLM 服务统一接口
支持云端 API 和本地 GPU 模型自动切换
"""
import requests
import os
from typing import Any, Dict, List, Optional
from app.config import settings


class CloudLLMService:
    """云端 LLM 服务（智谱AI）"""
    
    def __init__(self):
        self.api_key = settings.ZHIPU_API_KEY
        self.api_url = settings.ZHIPU_API_URL
        self.model = settings.ZHIPU_MODEL
    
    def chat(self, prompt: str, temperature: float = 0.1) -> str:
        """
        调用智谱AI API生成回答
        
        Args:
            prompt: 输入提示词
            temperature: 温度参数，控制随机性
        
        Returns:
            AI生成的回答文本
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"智谱AI API调用失败: {str(e)}")
    
    def chat_with_context(self, question: str, context: str) -> str:
        """
        基于检索到的上下文回答问题

        Args:
            question: 用户问题
            context: 检索到的上下文

        Returns:
            AI生成的回答
        """
        if not context or context.strip() == "无相关内容":
            return "❌ 未检索到与问题相关的知识库内容"

        prompt = f"""基于以下上下文，精准回答问题，答案必须来自上下文，不要编造内容：

上下文：
{context}

问题：{question}

请基于上下文回答，如果上下文中没有相关信息，请说明无法回答。"""

        return self.chat(prompt, temperature=0.1)

    def chat_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        原生 Function Calling：携带工具定义调用 API

        Args:
            messages: 消息列表（含 system / user / assistant / tool 角色）
            tools: OpenAI 格式的工具定义列表
            temperature: 温度参数

        Returns:
            模型返回的 message 对象（含 content 和 tool_calls 字段）
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "tools": tools,
            "tool_choice": "auto"
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]
        except Exception as e:
            raise Exception(f"智谱AI API调用失败: {str(e)}")


class LLMService:
    """
    LLM 服务统一接口
    根据配置自动选择云端 API 或本地 GPU 模型
    """
    
    def __init__(self):
        # 检查是否使用本地 LLM
        self.use_local = os.getenv('USE_LOCAL_LLM', 'false').lower() == 'true'
        
        if self.use_local:
            print("🚀 使用本地 GPU 模型")
            from app.services.local_llm_service import get_local_llm_service
            self.backend = get_local_llm_service()
        else:
            print("☁️  使用云端 API（智谱AI）")
            self.backend = CloudLLMService()
    
    def chat(self, prompt: str, temperature: float = 0.1) -> str:
        """
        生成回答（统一接口）
        
        Args:
            prompt: 输入提示词
            temperature: 温度参数
        
        Returns:
            AI生成的回答文本
        """
        return self.backend.chat(prompt, temperature)
    
    def chat_with_context(self, question: str, context: str) -> str:
        """
        基于检索到的上下文回答问题（统一接口）

        Args:
            question: 用户问题
            context: 检索到的上下文

        Returns:
            AI生成的回答
        """
        return self.backend.chat_with_context(question, context)

    def chat_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        原生 Function Calling（统一接口）

        Args:
            messages: 消息列表（含 system / user / assistant / tool 角色）
            tools: OpenAI 格式的工具定义列表
            temperature: 温度参数

        Returns:
            模型返回的 message 对象（含 content 和 tool_calls 字段）

        Raises:
            Exception: 当前后端不支持 Function Calling 时抛出
        """
        if not hasattr(self.backend, 'chat_with_tools'):
            raise Exception(
                f"当前 LLM 后端（{type(self.backend).__name__}）不支持 Function Calling，"
                "请使用云端 API（智谱AI）或切换到支持 tool calling 的本地推理框架（如 vLLM/Ollama）"
            )
        return self.backend.chat_with_tools(messages, tools, temperature)
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        if self.use_local and hasattr(self.backend, 'get_model_info'):
            return {
                "type": "local_gpu",
                **self.backend.get_model_info()
            }
        else:
            return {
                "type": "cloud_api",
                "provider": "zhipu_ai",
                "model": getattr(self.backend, 'model', 'unknown')
            }


# 创建全局实例
llm_service = LLMService()

