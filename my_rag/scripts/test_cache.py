"""
Redis 缓存功能测试脚本
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

def test_cache_health():
    """测试缓存健康状态"""
    print_section("1. 检查缓存服务状态")
    response = requests.get(f"{BASE_URL}/api/cache/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200

def test_cache_stats():
    """测试缓存统计"""
    print_section("2. 获取缓存统计信息")
    response = requests.get(f"{BASE_URL}/api/cache/stats")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200

def test_chat_with_cache():
    """测试带缓存的问答"""
    print_section("3. 测试问答缓存功能")
    
    question = "Python 是什么时候创建的？"
    
    # 第一次请求（缓存未命中）
    print(f"\n第一次请求: {question}")
    start_time = time.time()
    response1 = requests.post(
        f"{BASE_URL}/api/chat",
        json={"question": question}
    )
    time1 = time.time() - start_time
    
    if response1.status_code == 200:
        result1 = response1.json()
        print(f"✅ 响应时间: {time1:.3f}秒")
        print(f"回答: {result1['answer'][:100]}...")
    else:
        print(f"❌ 请求失败: {response1.text}")
        return False
    
    # 等待一下
    time.sleep(1)
    
    # 第二次请求（缓存命中）
    print(f"\n第二次请求（相同问题）: {question}")
    start_time = time.time()
    response2 = requests.post(
        f"{BASE_URL}/api/chat",
        json={"question": question}
    )
    time2 = time.time() - start_time
    
    if response2.status_code == 200:
        result2 = response2.json()
        print(f"✅ 响应时间: {time2:.3f}秒")
        print(f"回答: {result2['answer'][:100]}...")
        
        # 对比性能
        print(f"\n📊 性能对比:")
        print(f"  第一次（无缓存）: {time1:.3f}秒")
        print(f"  第二次（有缓存）: {time2:.3f}秒")
        speedup = (time1 - time2) / time1 * 100
        print(f"  性能提升: {speedup:.1f}%")
        
        # 验证答案一致性
        if result1['answer'] == result2['answer']:
            print(f"✅ 答案一致性验证通过")
        else:
            print(f"⚠️  答案不一致")
        
        return True
    else:
        print(f"❌ 请求失败: {response2.text}")
        return False

def test_clear_cache():
    """测试清空缓存"""
    print_section("4. 清空缓存")
    response = requests.delete(f"{BASE_URL}/api/cache/clear")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200

def main():
    """主测试函数"""
    print("=" * 60)
    print("  Redis 缓存功能测试")
    print("=" * 60)
    
    results = {}
    
    # 运行所有测试
    results["缓存健康检查"] = test_cache_health()
    results["缓存统计"] = test_cache_stats()
    results["问答缓存"] = test_chat_with_cache()
    results["清空缓存"] = test_clear_cache()
    
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
        print("🎉 所有测试通过！Redis 缓存功能正常！")
        print("\n📌 缓存管理接口:")
        print("  - 缓存统计: GET /api/cache/stats")
        print("  - 清空缓存: DELETE /api/cache/clear")
        print("  - 健康检查: GET /api/cache/health")
    else:
        print("⚠️  部分测试失败，请检查日志")
    print("=" * 60)

if __name__ == "__main__":
    main()
