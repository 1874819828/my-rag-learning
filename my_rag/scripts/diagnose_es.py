"""
Elasticsearch 诊断脚本
自动检测 ES 问题并提供解决方案
"""
import subprocess
import requests
import sys

def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_docker():
    """检查 Docker 是否运行"""
    print_section("1. 检查 Docker 状态")
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Docker 正在运行")
            return True
        else:
            print("❌ Docker 未运行或无法访问")
            return False
    except Exception as e:
        print(f"❌ Docker 检查失败: {str(e)}")
        return False

def check_es_container():
    """检查 ES 容器状态"""
    print_section("2. 检查 ES 容器")
    try:
        result = subprocess.run(
            ["docker", "ps", "-a"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if "elasticsearch" in result.stdout:
            if "Up" in result.stdout:
                print("✅ ES 容器正在运行")
                return "running"
            else:
                print("⚠️  ES 容器存在但未运行")
                return "stopped"
        else:
            print("❌ ES 容器不存在")
            return "not_found"
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return "error"

def check_es_connection():
    """检查 ES 连接"""
    print_section("3. 检查 ES 连接")
    try:
        response = requests.get("http://localhost:9200", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ES 连接成功")
            print(f"   版本: {data.get('version', {}).get('number', 'N/A')}")
            print(f"   集群: {data.get('cluster_name', 'N/A')}")
            return True
        else:
            print(f"⚠️  ES 响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 ES (localhost:9200)")
        return False
    except Exception as e:
        print(f"❌ 连接检查失败: {str(e)}")
        return False

def check_es_health():
    """检查 ES 健康状态"""
    print_section("4. 检查 ES 健康状态")
    try:
        response = requests.get("http://localhost:9200/_cluster/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            
            if status == 'green':
                print(f"✅ ES 健康状态: {status} (优秀)")
            elif status == 'yellow':
                print(f"⚠️  ES 健康状态: {status} (可用但有警告)")
            else:
                print(f"❌ ES 健康状态: {status} (异常)")
            
            print(f"   节点数: {data.get('number_of_nodes', 0)}")
            print(f"   数据节点: {data.get('number_of_data_nodes', 0)}")
            return status in ['green', 'yellow']
        else:
            print(f"❌ 无法获取健康状态")
            return False
    except Exception as e:
        print(f"❌ 健康检查失败: {str(e)}")
        return False

def check_network():
    """检查 Docker 网络"""
    print_section("5. 检查 Docker 网络")
    try:
        result = subprocess.run(
            ["docker", "network", "ls"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if "rag-network" in result.stdout:
            print("✅ rag-network 网络存在")
            return True
        else:
            print("❌ rag-network 网络不存在")
            return False
    except Exception as e:
        print(f"❌ 网络检查失败: {str(e)}")
        return False

def provide_solutions(container_status, es_connected):
    """提供解决方案"""
    print_section("诊断结果与建议")
    
    if container_status == "running" and es_connected:
        print("🎉 Elasticsearch 运行正常！")
        print("\n✅ 系统状态:")
        print("  - ES 容器: 运行中")
        print("  - ES 服务: 可访问")
        print("  - 混合检索: 可用")
        print("\n📌 下一步:")
        print("  1. 重启 FastAPI: python run.py")
        print("  2. 测试混合检索: python scripts/test_hybrid_search.py")
        return
    
    print("⚠️  Elasticsearch 存在问题\n")
    
    if container_status == "not_found":
        print("📋 问题: ES 容器不存在")
        print("\n💡 解决方案:")
        print("  1. 禁用 Docker 代理:")
        print("     - 打开 Docker Desktop")
        print("     - 设置 → Resources → Proxies")
        print("     - 取消勾选 'Manual proxy configuration'")
        print("     - Apply & Restart")
        print("\n  2. 拉取 ES 镜像:")
        print("     docker pull elasticsearch:8.11.0")
        print("\n  3. 启动 ES:")
        print("     docker-compose up -d elasticsearch")
        print("\n  或使用手动命令:")
        print("     docker run -d --name rag-elasticsearch \\")
        print("       --network rag-network \\")
        print("       -p 9200:9200 -p 9300:9300 \\")
        print("       -e 'discovery.type=single-node' \\")
        print("       -e 'xpack.security.enabled=false' \\")
        print("       -e 'ES_JAVA_OPTS=-Xms512m -Xmx512m' \\")
        print("       elasticsearch:8.11.0")
    
    elif container_status == "stopped":
        print("📋 问题: ES 容器已停止")
        print("\n💡 解决方案:")
        print("  1. 启动容器:")
        print("     docker start rag-elasticsearch")
        print("\n  2. 查看日志:")
        print("     docker logs rag-elasticsearch")
        print("\n  3. 如果启动失败，删除并重建:")
        print("     docker rm rag-elasticsearch")
        print("     docker-compose up -d elasticsearch")
    
    elif container_status == "running" and not es_connected:
        print("📋 问题: ES 容器运行但无法连接")
        print("\n💡 解决方案:")
        print("  1. 查看容器日志:")
        print("     docker logs rag-elasticsearch")
        print("\n  2. 检查端口映射:")
        print("     docker port rag-elasticsearch")
        print("\n  3. 重启容器:")
        print("     docker restart rag-elasticsearch")
        print("\n  4. 等待 ES 完全启动（可能需要 30-60 秒）")
    
    print("\n📚 详细文档: docs/ES_TROUBLESHOOTING.md")

def main():
    """主函数"""
    print("=" * 60)
    print("  Elasticsearch 诊断工具")
    print("=" * 60)
    
    # 运行诊断
    docker_ok = check_docker()
    if not docker_ok:
        print("\n❌ Docker 未运行，请先启动 Docker Desktop")
        sys.exit(1)
    
    network_ok = check_network()
    container_status = check_es_container()
    es_connected = False
    
    if container_status == "running":
        es_connected = check_es_connection()
        if es_connected:
            check_es_health()
    
    # 提供解决方案
    provide_solutions(container_status, es_connected)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
