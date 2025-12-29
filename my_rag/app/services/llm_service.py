"""
智谱AI LLM服务
"""
import requests
from typing import Optional
from app.config import settings

class LLMService:
    """智谱AI服务封装"""
    
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

# 创建全局实例
llm_service = LLMService()

