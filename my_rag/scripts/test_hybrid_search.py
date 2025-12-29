"""
混合检索功能测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_hybrid_search():
    """测试混合检索"""
    print_section("混合检索测试")
    
    question = "Python 有什么特点？"
    
    print(f"\n问题: {question}")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"question": question}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 回答: {result['answer']}")
        print(f"会话ID: {result['session_id']}")
        return True
    else:
        print(f"❌ 请求失败: {response.text}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("  混合检索功能测试")
    print("=" * 60)
    print("\n注意: 如果 Elasticsearch 未启动，将自动降级为纯向量检索")
    
    success = test_hybrid_search()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 测试通过！")
        print("\n📌 说明:")
        print("  - ES 可用时：使用混合检索（向量 + 关键词）")
        print("  - ES 不可用时：自动降级为纯向量检索")
    else:
        print("⚠️  测试失败")
    print("=" * 60)

if __name__ == "__main__":
    main()
