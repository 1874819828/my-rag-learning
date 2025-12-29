"""
端到端测试脚本
测试完整的 RAG 工作流程：上传文档 -> 问答 -> 查看历史
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_health():
    """测试健康检查"""
    print_section("1. 健康检查")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.status_code == 200

def test_upload():
    """测试文档上传"""
    print_section("2. 上传测试文档")
    
    # 创建测试文档
    test_content = """
Python 是一种高级编程语言。
它由 Guido van Rossum 于 1991 年创建。
Python 以其简洁的语法和强大的功能而闻名。
Python 广泛应用于 Web 开发、数据科学、人工智能等领域。
"""
    
    # 保存为临时文件
    with open("test_doc.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    # 上传文件
    with open("test_doc.txt", "rb") as f:
        files = {"file": ("test_doc.txt", f, "text/plain")}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"文档ID: {result['document_id']}")
        print(f"文件名: {result['filename']}")
        print(f"状态: {result['status']}")
        return True
    else:
        print(f"错误: {response.text}")
        return False

def test_chat():
    """测试问答功能"""
    print_section("3. 测试问答")
    
    questions = [
        "Python 是什么时候创建的？",
        "Python 有什么特点？",
        "Python 可以用在哪些领域？"
    ]
    
    session_id = None
    
    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}: {question}")
        
        payload = {"question": question}
        if session_id:
            payload["session_id"] = session_id
        
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"回答: {result['answer']}")
            print(f"会话ID: {result['session_id']}")
            session_id = result['session_id']
        else:
            print(f"错误: {response.text}")
            return False
        
        time.sleep(1)  # 避免请求过快
    
    return True

def test_conversation_list():
    """测试会话列表"""
    print_section("4. 查看会话列表")
    
    response = requests.get(f"{BASE_URL}/api/conversation/list")
    
    if response.status_code == 200:
        conversations = response.json()
        print(f"会话总数: {len(conversations)}")
        
        if conversations:
            print("\n最近的会话:")
            for conv in conversations[:3]:
                print(f"  - ID: {conv['session_id']}")
                print(f"    标题: {conv['title']}")
                print(f"    创建时间: {conv['created_at']}")
        return True
    else:
        print(f"错误: {response.text}")
        return False

def test_milvus_data():
    """测试 Milvus 数据"""
    print_section("5. 查看 Milvus 数据")
    
    try:
        from pymilvus import MilvusClient
        from app.config import settings
        
        client = MilvusClient(f"tcp://{settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
        collection_name = settings.MILVUS_COLLECTION_NAME
        
        if client.has_collection(collection_name):
            stats = client.get_collection_stats(collection_name)
            print(f"集合名称: {collection_name}")
            print(f"数据条数: {stats.get('row_count', 'N/A')}")
            return True
        else:
            print(f"集合 {collection_name} 不存在")
            return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("  RAG 系统端到端测试")
    print("=" * 60)
    
    results = {}
    
    # 运行所有测试
    results["健康检查"] = test_health()
    results["文档上传"] = test_upload()
    
    # 等待文档处理完成
    print("\n⏳ 等待文档处理（5秒）...")
    time.sleep(5)
    
    results["问答功能"] = test_chat()
    results["会话列表"] = test_conversation_list()
    results["Milvus数据"] = test_milvus_data()
    
    # 汇总结果
    print_section("测试结果汇总")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20s} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！RAG 系统运行正常！")
        print("\n📌 你可以访问:")
        print("  - API 文档: http://localhost:8000/docs")
        print("  - 在 Swagger UI 中测试更多功能")
    else:
        print("⚠️  部分测试失败，请检查日志")
    print("=" * 60)

if __name__ == "__main__":
    main()
