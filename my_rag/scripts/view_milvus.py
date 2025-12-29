"""
查看 Milvus 数据的简单脚本
替代 Attu Web UI
"""
from pymilvus import MilvusClient
from app.config import settings

def view_milvus_data():
    """查看 Milvus 集合数据"""
    try:
        # 连接 Milvus
        client = MilvusClient(f"tcp://{settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
        collection_name = settings.MILVUS_COLLECTION_NAME
        
        print("=" * 60)
        print("Milvus 数据查看工具")
        print("=" * 60)
        
        # 检查集合是否存在
        if not client.has_collection(collection_name):
            print(f"\n❌ 集合 '{collection_name}' 不存在")
            print("提示：请先上传文档以创建集合")
            return
        
        print(f"\n✅ 集合名称: {collection_name}")
        
        # 获取集合统计信息
        stats = client.get_collection_stats(collection_name)
        print(f"📊 数据条数: {stats.get('row_count', 'N/A')}")
        
        # 查询前 10 条数据
        print("\n" + "=" * 60)
        print("前 10 条数据预览:")
        print("=" * 60)
        
        results = client.query(
            collection_name=collection_name,
            filter="",
            output_fields=["content"],
            limit=10
        )
        
        if not results:
            print("\n暂无数据")
        else:
            for idx, item in enumerate(results, 1):
                content = item.get("content", "")
                # 截断显示
                display_content = content[:100] + "..." if len(content) > 100 else content
                print(f"\n[{idx}] {display_content}")
        
        print("\n" + "=" * 60)
        print("提示：访问 http://localhost:8000/docs 使用 FastAPI 接口")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        print("\n可能的原因：")
        print("1. Milvus 服务未启动")
        print("2. 连接配置错误")
        print("3. 集合尚未创建（需要先上传文档）")

if __name__ == "__main__":
    view_milvus_data()
