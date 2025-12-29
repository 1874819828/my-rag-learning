"""
部署测试脚本
验证所有服务是否正常运行
"""
import requests
import time
import sys
from pymilvus import MilvusClient
import pymysql
import redis

def test_fastapi():
    """测试 FastAPI 服务"""
    print("🔍 测试 FastAPI 服务...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI 服务正常")
            return True
        else:
            print(f"❌ FastAPI 服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FastAPI 连接失败: {str(e)}")
        return False

def test_mysql():
    """测试 MySQL 连接"""
    print("🔍 测试 MySQL 连接...")
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='root123',
            database='rag_db',
            connect_timeout=5
        )
        conn.close()
        print("✅ MySQL 连接正常")
        return True
    except Exception as e:
        print(f"❌ MySQL 连接失败: {str(e)}")
        return False

def test_milvus():
    """测试 Milvus 连接"""
    print("🔍 测试 Milvus 连接...")
    try:
        client = MilvusClient("tcp://localhost:19530")
        # 简单测试连接
        collections = client.list_collections()
        print(f"✅ Milvus 连接正常 (集合数: {len(collections)})")
        return True
    except Exception as e:
        print(f"❌ Milvus 连接失败: {str(e)}")
        return False

def test_redis():
    """测试 Redis 连接"""
    print("🔍 测试 Redis 连接...")
    try:
        r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=5)
        r.ping()
        print("✅ Redis 连接正常")
        return True
    except Exception as e:
        print(f"❌ Redis 连接失败: {str(e)}")
        return False

def test_api_endpoints():
    """测试 API 端点"""
    print("🔍 测试 API 端点...")
    try:
        # 测试根路径
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print(f"❌ 根路径测试失败: {response.status_code}")
            return False
        
        # 测试文档页面
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code != 200:
            print(f"❌ 文档页面测试失败: {response.status_code}")
            return False
        
        print("✅ API 端点测试通过")
        return True
    except Exception as e:
        print(f"❌ API 端点测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("RAG 系统部署测试")
    print("=" * 60)
    print()
    
    # 等待服务启动
    print("⏳ 等待服务启动（10秒）...")
    time.sleep(10)
    print()
    
    # 运行所有测试
    results = {
        "FastAPI": test_fastapi(),
        "MySQL": test_mysql(),
        "Milvus": test_milvus(),
        "Redis": test_redis(),
        "API Endpoints": test_api_endpoints()
    }
    
    print()
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for service, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{service:20s} {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 所有测试通过！系统部署成功！")
        print()
        print("📌 访问地址:")
        print("  - FastAPI 文档: http://localhost:8000/docs")
        print("  - FastAPI API: http://localhost:8000")
        print("  - Attu (如已启动): http://localhost:8001")
        return 0
    else:
        print("⚠️  部分测试失败，请检查服务状态")
        print()
        print("💡 故障排查:")
        print("  1. 检查服务状态: docker-compose ps")
        print("  2. 查看日志: docker-compose logs -f")
        print("  3. 重启服务: docker-compose restart")
        return 1

if __name__ == "__main__":
    sys.exit(main())
