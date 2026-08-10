"""
Rerank 精排服务
使用 Cross-Encoder（BGE-reranker）对召回结果做精排。

流水线位置：多路召回 → RRF 融合 → 【Rerank 精排】 → 阈值过滤 → 截断 TopK

与 Embedding（Bi-Encoder）的区别：
- Embedding：query 和 doc 分别编码，再算余弦，快但粗
- Rerank：query 和 doc 拼接后过 Cross-Encoder，成对精算，慢但准
"""
import os
import math
from typing import List, Dict, Any, Optional

from app.config import settings


def _sigmoid(x: float) -> float:
    """数值稳定的 sigmoid，避免 math.exp 溢出"""
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


class RerankService:
    """Cross-Encoder 精排服务"""

    def __init__(self):
        self.enabled = settings.RERANK_ENABLED
        self._model = None
        self._load_error = None

    @property
    def model(self):
        """延迟加载 rerank 模型，失败时降级为 None"""
        if self._model is None and self._load_error is None:
            try:
                from sentence_transformers import CrossEncoder

                # 优先本地模型路径，与 embedding 模型加载策略一致
                local_model_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    'models', 'bge-reranker-base'
                )
                if os.path.exists(local_model_path):
                    print(f"✅ 使用本地 rerank 模型: {local_model_path}")
                    model_path = local_model_path
                else:
                    print(f"⚠️  本地 rerank 模型不存在，尝试下载: {settings.RERANK_MODEL}")
                    model_path = settings.RERANK_MODEL

                self._model = CrossEncoder(model_path, max_length=512)
                print("✅ Rerank 模型加载完成")
            except Exception as e:
                self._load_error = str(e)
                print(f"⚠️  Rerank 模型加载失败，将降级为 RRF 排序: {e}")
        return self._model

    def rerank(
        self,
        query: str,
        docs: List[str],
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Cross-Encoder 精排 + 阈值过滤

        Args:
            query: 查询文本
            docs: 候选文档内容列表
            top_k: 返回数量上限（默认读配置）
            score_threshold: 概率阈值 0~1，低于此值丢弃（默认读配置）

        Returns:
            精排结果，每项含 content 和 rerank_score（0~1 概率）
        """
        if not docs:
            return []

        # 模型不可用 → 降级，原序返回（不截断，交给上层 _finalize 处理）
        if not self.enabled or self.model is None:
            return [{"content": d, "rerank_score": 0.0} for d in docs]

        top_k = top_k or settings.RERANK_TOP_K
        if score_threshold is None:
            score_threshold = settings.RERANK_SCORE_THRESHOLD

        try:
            # Cross-Encoder 成对打分
            pairs = [(query, doc) for doc in docs]
            logits = self.model.predict(pairs)

            # BGE-reranker 输出 logit，转 sigmoid 概率，便于设阈值
            probs = [_sigmoid(float(s)) for s in logits]

            # 按概率降序
            ranked = sorted(zip(docs, probs), key=lambda x: x[1], reverse=True)

            # 阈值过滤 + 截断 top_k
            results: List[Dict[str, Any]] = []
            for doc, prob in ranked:
                if prob < score_threshold:
                    continue
                results.append({"content": doc, "rerank_score": prob})
                if len(results) >= top_k:
                    break

            print(f"🎯 Rerank 精排: {len(docs)} → {len(results)} 条 (阈值={score_threshold})")
            return results
        except Exception as e:
            print(f"⚠️  Rerank 打分失败，降级为原始顺序: {e}")
            return [{"content": d, "rerank_score": 0.0} for d in docs]


# 全局实例
rerank_service = RerankService()
