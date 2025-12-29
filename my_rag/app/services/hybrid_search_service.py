"""
混合检索服务
结合向量检索（Milvus）和关键词检索（Elasticsearch）
"""
from typing import List, Dict, Any
from app.services.milvus_service import milvus_service
from app.services.elasticsearch_service import es_service

class HybridSearchService:
    """混合检索服务"""
    
    def __init__(self):
        self.milvus = milvus_service
        self.es = es_service
    
    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        vector_weight: float = 0.6,
        keyword_weight: float = 0.4
    ) -> List[Dict[str, Any]]:
        """
        混合检索：结合向量检索和关键词检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            vector_weight: 向量检索权重
            keyword_weight: 关键词检索权重
        
        Returns:
            融合后的检索结果
        """
        # 1. 向量检索（Milvus）
        vector_results = self.milvus.search(query, top_k=top_k * 2)
        
        # 2. 关键词检索（Elasticsearch）
        keyword_results = []
        if self.es.enabled:
            keyword_results = self.es.search(query, top_k=top_k * 2)
        
        # 3. 结果融合（RRF - Reciprocal Rank Fusion）
        fused_results = self._reciprocal_rank_fusion(
            vector_results,
            keyword_results,
            vector_weight,
            keyword_weight
        )
        
        # 4. 返回 Top K
        return fused_results[:top_k]
    
    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        vector_weight: float = 0.6,
        keyword_weight: float = 0.4,
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """
        RRF（Reciprocal Rank Fusion）算法融合结果
        
        Args:
            vector_results: 向量检索结果
            keyword_results: 关键词检索结果
            vector_weight: 向量检索权重
            keyword_weight: 关键词检索权重
            k: RRF 参数
        
        Returns:
            融合后的结果
        """
        # 使用内容作为唯一标识
        scores = {}
        contents = {}
        
        # 处理向量检索结果
        for rank, result in enumerate(vector_results, 1):
            content = result.get('content', '')
            if content:
                rrf_score = vector_weight / (k + rank)
                scores[content] = scores.get(content, 0) + rrf_score
                contents[content] = result
        
        # 处理关键词检索结果
        for rank, result in enumerate(keyword_results, 1):
            content = result.get('content', '')
            if content:
                rrf_score = keyword_weight / (k + rank)
                scores[content] = scores.get(content, 0) + rrf_score
                if content not in contents:
                    contents[content] = result
        
        # 按分数排序
        sorted_contents = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 构建最终结果
        fused_results = []
        for content, score in sorted_contents:
            result = contents[content].copy()
            result['fused_score'] = score
            fused_results.append(result)
        
        return fused_results
    
    def search_context(
        self,
        query: str,
        top_k: int = 3,
        use_hybrid: bool = True
    ) -> str:
        """
        检索并返回拼接的上下文文本
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            use_hybrid: 是否使用混合检索
        
        Returns:
            拼接后的上下文文本
        """
        if use_hybrid and self.es.enabled:
            # 使用混合检索
            results = self.hybrid_search(query, top_k=top_k)
            print(f"🔍 混合检索: 返回 {len(results)} 条结果")
        else:
            # 仅使用向量检索
            results = self.milvus.search(query, top_k=top_k)
            print(f"🔍 向量检索: 返回 {len(results)} 条结果")
        
        if not results:
            return "无相关内容"
        
        # 拼接上下文
        context_parts = []
        for idx, result in enumerate(results, 1):
            content = result.get('content', '')
            score = result.get('fused_score') or result.get('distance') or result.get('score', 0)
            context_parts.append(f"[片段{idx}] {content}")
        
        context = "\n\n".join(context_parts)
        return context

# 创建全局实例
hybrid_search_service = HybridSearchService()
