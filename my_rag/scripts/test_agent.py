"""
Agent 功能测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_agent_tools():
    """测试获取工具列表"""
    print_section("1. 获取 Agent 工具列表")
    response = requests.get(f"{BASE_URL}/api/agent/tools")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 工具数量: {result['count']}")
        print("\n可用工具:")
        for tool in result['tools']:
            print(f"  - {tool['name']}: {tool['description']}")
        return True
    else:
        print(f"❌ 请求失败: {response.text}")
        return False

def test_agent_search():
    """测试 Agent 搜索知识库"""
    print_section("2. Agent 搜索知识库")
    
    question = "Python 是什么时候创建的？"
    print(f"\n问题: {question}")
    
    response = requests.post(
        f"{BASE_URL}/api/agent/chat",
        json={"question": question}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功: {result['success']}")
        print(f"回答: {result['answer']}")
        print(f"工具调用次数: {result['tool_calls']}")
        return True
    else:
        print(f"❌ 请求失败: {response.text}")
        return False

def test_agent_calculator():
    """测试 Agent 计算器"""
    print_section("3. Agent 计算器")
    
    question = "计算 123 + 456 * 2"
    print(f"\n问题: {question}")
    
    response = requests.post(
        f"{BASE_URL}/api/agent/chat",
        json={"question": question}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功: {result['success']}")
        print(f"回答: {result['answer']}")
        print(f"工具调用次数: {result['tool_calls']}")
        return True
    else:
        print(f"❌ 请求失败: {response.text}")
        return False

def test_agent_time():
    """测试 Agent 时间工具"""
    print_section("4. Agent 时间工具")
    
    question = "现在几点了？"
    print(f"\n问题: {question}")
    
    response = requests.post(
        f"{BASE_URL}/api/agent/chat",
        json={"question": question}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功: {result['success']}")
        print(f"回答: {result['answer']}")
        print(f"工具调用次数: {result['tool_calls']}")
        return True
    else:
        print(f"❌ 请求失败: {response.text}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("  Agent 功能测试")
    print("=" * 60)
    
    results = {}
    
    # 运行所有测试
    results["工具列表"] = test_agent_tools()
    results["搜索知识库"] = test_agent_search()
    results["计算器"] = test_agent_calculator()
    results["时间工具"] = test_agent_time()
    
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
        print("🎉 所有测试通过！Agent 功能正常！")
        print("\n📌 Agent 特性:")
        print("  - 自动选择合适的工具")
        print("  - 支持多步推理")
        print("  - 可扩展工具集")
    else:
        print("⚠️  部分测试失败，请检查日志")
    print("=" * 60)

if __name__ == "__main__":
    main()
