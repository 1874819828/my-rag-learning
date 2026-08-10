"""
验证 Rerank + 混合检索流水线逻辑（完全自包含，不依赖项目 venv / Milvus / ES / 模型）
运行: python scripts/test_rerank.py
"""
import os
import sys
import types
import importlib.util
from unittest.mock import MagicMock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICES = os.path.join(ROOT, 'app', 'services')


# ---------- 1. 构造 fake app.config（绕过 pydantic_settings）----------
class _FakeSettings:
    RERANK_ENABLED = False          # 关闭，避免下载模型
    RERANK_MODEL = "BAAI/bge-reranker-base"
    RECALL_TOP_K = 30
    RERANK_TOP_K = 5
    RERANK_SCORE_THRESHOLD = 0.3
    VECTOR_DISTANCE_THRESHOLD = 0.5
    VECTOR_WEIGHT = 0.6
    KEYWORD_WEIGHT = 0.4

    def __getattr__(self, name):
        # 其它配置项（MILVUS_HOST 等）实例化时只是被引用，返回 MagicMock 即可
        return MagicMock()


fake_config = types.ModuleType('app.config')
fake_config.settings = _FakeSettings()
sys.modules['app'] = types.ModuleType('app')
sys.modules['app.services'] = types.ModuleType('app.services')
sys.modules['app.config'] = fake_config

# ---------- 2. Stub 外部依赖 ----------
for m in ['elasticsearch', 'elasticsearch.helpers', 'pymilvus', 'sentence_transformers']:
    sys.modules[m] = MagicMock()


# ---------- 3. 用 importlib 手动加载服务模块 ----------
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


load('app.services.milvus_service', os.path.join(SERVICES, 'milvus_service.py'))
load('app.services.elasticsearch_service', os.path.join(SERVICES, 'elasticsearch_service.py'))
rerank_mod = load('app.services.rerank_service', os.path.join(SERVICES, 'rerank_service.py'))
hybrid_mod = load('app.services.hybrid_search_service', os.path.join(SERVICES, 'hybrid_search_service.py'))

_sigmoid = rerank_mod._sigmoid
rerank_service = rerank_mod.rerank_service
HybridSearchService = hybrid_mod.HybridSearchService


# ---------- 4. 测试用例 ----------
def test_sigmoid():
    assert abs(_sigmoid(0.0) - 0.5) < 1e-9
    assert _sigmoid(100.0) > 0.99999
    assert _sigmoid(-100.0) < 1e-4
    print("✅ test_sigmoid 通过")


def test_rerank_degradation():
    docs = ["docA", "docB", "docC"]
    out = rerank_service.rerank("query", docs, top_k=2)
    assert len(out) == 3, f"降级应原序返回全部, got {len(out)}"
    assert all(d["rerank_score"] == 0.0 for d in out)
    print("✅ test_rerank_degradation 通过")


def test_rrf():
    svc = HybridSearchService.__new__(HybridSearchService)
    vec = [{"content": "A"}, {"content": "B"}, {"content": "C"}]
    kw = [{"content": "B"}, {"content": "D"}]
    fused = svc._reciprocal_rank_fusion(vec, kw, 0.6, 0.4, k=60)
    assert fused[0]["content"] == "B", f"双路命中的 B 应排第一, got {fused[0]}"
    assert "fused_score" in fused[0]
    print(f"✅ test_rrf 通过 (B fused_score={fused[0]['fused_score']:.6f})")


def test_finalize_truncate():
    svc = HybridSearchService.__new__(HybridSearchService)
    svc.rerank = rerank_service  # enabled=False
    cands = [{"content": f"doc{i}"} for i in range(10)]
    out = svc._finalize("q", cands, top_k=3)
    assert len(out) == 3
    print("✅ test_finalize_truncate 通过")


def test_finalize_rerank_mock():
    svc = HybridSearchService.__new__(HybridSearchService)
    mock_rerank = MagicMock()
    mock_rerank.enabled = True
    mock_rerank.model = MagicMock()  # 非 None
    mock_rerank.rerank.return_value = [
        {"content": "doc2", "rerank_score": 0.9},
        {"content": "doc0", "rerank_score": 0.8},
    ]
    svc.rerank = mock_rerank
    cands = [
        {"content": "doc0", "document_id": 1},
        {"content": "doc1", "document_id": 2},
        {"content": "doc2", "document_id": 3},
    ]
    out = svc._finalize("q", cands, top_k=2)
    assert len(out) == 2
    assert out[0]["content"] == "doc2"
    assert out[0]["rerank_score"] == 0.9
    assert out[0]["document_id"] == 3  # 元信息已合并
    print("✅ test_finalize_rerank_mock 通过 (元信息已合并)")


def test_vector_finalize_threshold():
    svc = HybridSearchService.__new__(HybridSearchService)
    svc.rerank = rerank_service  # disabled
    cands = [
        {"content": "high", "distance": 0.9},
        {"content": "low", "distance": 0.1},
        {"content": "mid", "distance": 0.6},
    ]
    out = svc._vector_finalize("q", cands, top_k=3)
    contents = [r["content"] for r in out]
    assert "low" not in contents, "distance 0.1 应被阈值过滤"
    assert "high" in contents and "mid" in contents
    print(f"✅ test_vector_finalize_threshold 通过 (保留 {contents})")


if __name__ == "__main__":
    test_sigmoid()
    test_rerank_degradation()
    test_rrf()
    test_finalize_truncate()
    test_finalize_rerank_mock()
    test_vector_finalize_threshold()
    print("\n🎉 全部测试通过")
