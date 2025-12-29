"""
Redis 缓存服务
用于缓存问答结果，提升响应速度
"""
import redis
import json
import hashlib
from typing import Optional, Dict, Any
from app.config import settings

class CacheService:
    """Redis 缓存服务"""
    
    def __init__(self):
        """初始化 Redis 连接"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # 测试连接
            self.redis_client.ping()
            self.enabled = True
            print("✅ Redis 缓存服务已启用")
        except Exception as e:
            print(f"⚠️  Redis 连接失败，缓存功能已禁用: {str(e)}")
            self.redis_client = None
            self.enabled = False
    
    def _generate_cache_key(self, question: str, context: str = "") -> str:
        """
        生成缓存键
        
        Args:
            question: 用户问题
            context: 上下文（可选）
        
        Returns:
            缓存键
        """
        # 使用问题和上下文的哈希作为键
        content = f"{question}:{context}"
        hash_key = hashlib.md5(content.encode('utf-8')).hexdigest()
        return f"rag:chat:{hash_key}"
    
    def get_cached_answer(self, question: str, context: str = "") -> Optional[str]:
        """
        获取缓存的答案
        
        Args:
            question: 用户问题
            context: 上下文
        
        Returns:
            缓存的答案，如果不存在返回 None
        """
        if not self.enabled:
            return None
        
        try:
            cache_key = self._generate_cache_key(question, context)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                print(f"✅ 缓存命中: {cache_key[:20]}...")
                return data.get("answer")
            
            return None
        except Exception as e:
            print(f"⚠️  缓存读取失败: {str(e)}")
            return None
    
    def set_cached_answer(
        self,
        question: str,
        answer: str,
        context: str = "",
        ttl: int = 3600
    ) -> bool:
        """
        设置缓存答案
        
        Args:
            question: 用户问题
            answer: AI 答案
            context: 上下文
            ttl: 过期时间（秒），默认 1 小时
        
        Returns:
            是否设置成功
        """
        if not self.enabled:
            return False
        
        try:
            cache_key = self._generate_cache_key(question, context)
            cache_data = {
                "question": question,
                "answer": answer,
                "context": context[:200],  # 只存储部分上下文
                "timestamp": self._get_timestamp()
            }
            
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data, ensure_ascii=False)
            )
            print(f"✅ 缓存已设置: {cache_key[:20]}... (TTL: {ttl}s)")
            return True
        except Exception as e:
            print(f"⚠️  缓存写入失败: {str(e)}")
            return False
    
    def delete_cache(self, question: str, context: str = "") -> bool:
        """
        删除指定缓存
        
        Args:
            question: 用户问题
            context: 上下文
        
        Returns:
            是否删除成功
        """
        if not self.enabled:
            return False
        
        try:
            cache_key = self._generate_cache_key(question, context)
            result = self.redis_client.delete(cache_key)
            return result > 0
        except Exception as e:
            print(f"⚠️  缓存删除失败: {str(e)}")
            return False
    
    def clear_all_cache(self) -> int:
        """
        清空所有 RAG 相关缓存
        
        Returns:
            删除的缓存数量
        """
        if not self.enabled:
            return 0
        
        try:
            # 查找所有 rag:chat: 开头的键
            keys = self.redis_client.keys("rag:chat:*")
            if keys:
                count = self.redis_client.delete(*keys)
                print(f"✅ 已清空 {count} 条缓存")
                return count
            return 0
        except Exception as e:
            print(f"⚠️  缓存清空失败: {str(e)}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计数据
        """
        if not self.enabled:
            return {
                "enabled": False,
                "message": "Redis 缓存未启用"
            }
        
        try:
            # 获取所有 RAG 缓存键
            keys = self.redis_client.keys("rag:chat:*")
            
            # 获取 Redis 信息
            info = self.redis_client.info()
            
            return {
                "enabled": True,
                "total_keys": len(keys),
                "memory_used": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "uptime_days": info.get("uptime_in_days", 0)
            }
        except Exception as e:
            return {
                "enabled": False,
                "error": str(e)
            }
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()

# 创建全局实例
cache_service = CacheService()
