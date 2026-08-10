"""
混合检索服务
结合向量检索（Milvus）和关键词检索（Elasticsearch）

流水线：多路召回（扩量）→ RRF 融合 → Rerank 精排 → 阈值过滤 → 截断 TopK
"""
from typing import List, Dict, Any, Optional

from app.services.milvus_service import milvus_service
from app.services.elasticsearch_service import es_service
from app.services.rerank_service import rerank_service
from app.config import settings


class HybridSearchService:
    """混合检索服务"""

    def __init__(self):
        self.milvus = milvus_service
        self.es = es_service
        self.rerank = rerank_service

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        vector_weight: Optional[float] = None,
        keyword_weight: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        混合检索：向量 + 关键词 → RRF 融合 → Rerank 精排

        Args:
            query: 查询文本
            top_k: 最终返回结果数
            vector_weight: 向量检索权重（默认读配置）
            keyword_weight: 关键词检索权重（默认读配置）

        Returns:
            精排后的结果列表
        """
        if vector_weight is None:
            vector_weight = settings.VECTOR_WEIGHT
        if keyword_weight is None:
            keyword_weight = settings.KEYWORD_WEIGHT

        # 1. 多路召回（扩量：用 RECALL_TOP_K，而非 top_k*2）
        recall_k = settings.RECALL_TOP_K
        vector_results = self.milvus.search(query, top_k=recall_k)
        keyword_results = []
        if self.es.enabled:
            keyword_results = self.es.search(query, top_k=recall_k)

        # 2. RRF 融合
        fused_results = self._reciprocal_rank_fusion(
            vector_results,
            keyword_results,
            vector_weight,
            keyword_weight,
        )

        # 3. Rerank 精排 + 截断（rerank 内部含阈值过滤）
        return self._finalize(query, fused_results, top_k)

    def _finalize(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        对候选结果做 Rerank 精排或直接截断

        - 开启 rerank 且模型可用：Cross-Encoder 精排 + 概率阈值过滤
        - 否则：直接截断 top_k（RRF 分数无量纲，不做阈值过滤）
        """
        if not candidates:
            return []

        if self.rerank.enabled and self.rerank.model is not None:
            docs = [r.get('content', '') for r in candidates]
            reranked = self.rerank.rerank(query, docs, top_k=top_k)

            # 合并原始元信息（document_id 等），保留 rerank_score
            meta_by_content = {r.get('content', ''): r for r in candidates}
            merged: List[Dict[str, Any]] = []
            for item in reranked:
                base = meta_by_content.get(item['content'], {})
                row = {k: v for k, v in base.items() if k != 'rerank_score'}
                row['content'] = item['content']
                row['rerank_score'] = item['rerank_score']
                merged.append(row)
            return merged

        return candidates[:top_k]

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        vector_weight: float = 0.6,
        keyword_weight: float = 0.4,
        k: int = 60,
    ) -> List[Dict[str, Any]]:
        """
        RRF（Reciprocal Rank Fusion）算法融合结果

        Args:
            vector_results: 向量检索结果
            keyword_results: 关键词检索结果
            vector_weight: 向量检索权重
            keyword_weight: 关键词检索权重
            k: RRF 平滑常数

        Returns:
            融合后的结果（按 fused_score 降序）
        """
        scores: Dict[str, float] = {}
        contents: Dict[str, Dict[str, Any]] = {}

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
        sorted_contents = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # 构建最终结果
        fused_results: List[Dict[str, Any]] = []
        for content, score in sorted_contents:
            result = contents[content].copy()
            result['fused_score'] = score
            fused_results.append(result)

        return fused_results

    def search_context(
        self,
        query: str,
        top_k: int = 3,
        use_hybrid: bool = True,
    ) -> str:
        """
        检索并返回拼接的上下文文本

        Args:
            query: 查询文本
            top_k: 最终返回结果数
            use_hybrid: 是否使用混合检索

        Returns:
            拼接后的上下文文本
        """
        if use_hybrid and self.es.enabled:
            # 混合检索：召回扩量 → RRF → Rerank
            results = self.hybrid_search(query, top_k=top_k)
            print(f"🔍 混合检索: 返回 {len(results)} 条结果")
        else:
            # 纯向量召回（扩量）→ rerank / 阈值过滤
            recall_k = settings.RECALL_TOP_K
            raw = self.milvus.search(query, top_k=recall_k)
            results = self._vector_finalize(query, raw, top_k)
            print(f"🔍 向量检索: 返回 {len(results)} 条结果")

        if not results:
            return "无相关内容"

        # 拼接上下文
        context_parts = []
        for idx, result in enumerate(results, 1):
            content = result.get('content', '')
            context_parts.append(f"[片段{idx}] {content}")

        return "\n\n".join(context_parts)

    def _vector_finalize(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        纯向量路径收尾：rerank 或 COSINE 阈值过滤

        - 开启 rerank：Cross-Encoder 精排 + 概率阈值（复用 _finalize）
        - 否则：按 COSINE distance 阈值过滤（方案3，distance 越大越相似）
        """
        if not candidates:
            return []

        if self.rerank.enabled and self.rerank.model is not None:
            return self._finalize(query, candidates, top_k)

        # 无 rerank：COSINE 相似度阈值过滤
        filtered = [
            r for r in candidates
            if r.get('distance', 0.0) >= settings.VECTOR_DISTANCE_THRESHOLD
        ]
        return (filtered or candidates)[:top_k]


# 全局实例
hybrid_search_service = HybridSearchService()
