"""
Elasticsearch 服务
用于关键词检索（BM25 算法）
"""
from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch
from app.config import settings

class ElasticsearchService:
    """Elasticsearch 关键词检索服务"""
    
    def __init__(self):
        """初始化 Elasticsearch 连接"""
        try:
            # Elasticsearch 8.x 兼容配置
            self.es_client = Elasticsearch(
                hosts=[f"http://{settings.ES_HOST}:{settings.ES_PORT}"],
                verify_certs=False,
                request_timeout=30,
                # 兼容性设置：使用 v8 API
                headers={"Accept": "application/vnd.elasticsearch+json; compatible-with=8"}
            )
            # 测试连接 - 使用 info() 而不是 ping()
            info = self.es_client.info()
            self.enabled = True
            print(f"✅ Elasticsearch 服务已启用 (版本: {info['version']['number']})")
        except Exception as e:
            print(f"⚠️  Elasticsearch 连接失败: {str(e)}")
            self.es_client = None
            self.enabled = False
        
        self.index_name = settings.ES_INDEX_NAME
    
    def create_index_if_not_exists(self):
        """创建索引（如果不存在）"""
        if not self.enabled:
            return False
        
        try:
            if not self.es_client.indices.exists(index=self.index_name):
                # 定义索引映射
                mapping = {
                    "mappings": {
                        "properties": {
                            "content": {
                                "type": "text",
                                "analyzer": "standard",
                                "fields": {
                                    "keyword": {
                                        "type": "keyword"
                                    }
                                }
                            },
                            "document_id": {
                                "type": "integer"
                            },
                            "chunk_id": {
                                "type": "integer"
                            },
                            "created_at": {
                                "type": "date"
                            }
                        }
                    },
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0,
                        "analysis": {
                            "analyzer": {
                                "default": {
                                    "type": "standard"
                                }
                            }
                        }
                    }
                }
                
                self.es_client.indices.create(
                    index=self.index_name,
                    body=mapping
                )
                print(f"✅ 创建 Elasticsearch 索引: {self.index_name}")
                return True
            return True
        except Exception as e:
            print(f"❌ 创建索引失败: {str(e)}")
            return False
    
    def index_document(
        self,
        content: str,
        document_id: int,
        chunk_id: int = 0
    ) -> bool:
        """
        索引单个文档
        
        Args:
            content: 文档内容
            document_id: 文档ID
            chunk_id: 文档块ID
        
        Returns:
            是否索引成功
        """
        if not self.enabled:
            return False
        
        try:
            self.create_index_if_not_exists()
            
            doc = {
                "content": content,
                "document_id": document_id,
                "chunk_id": chunk_id,
                "created_at": self._get_timestamp()
            }
            
            self.es_client.index(
                index=self.index_name,
                document=doc
            )
            return True
        except Exception as e:
            print(f"❌ 索引文档失败: {str(e)}")
            return False
    
    def index_documents_bulk(
        self,
        chunks: List[str],
        document_id: int
    ) -> int:
        """
        批量索引文档
        
        Args:
            chunks: 文档块列表
            document_id: 文档ID
        
        Returns:
            成功索引的数量
        """
        if not self.enabled:
            return 0
        
        try:
            self.create_index_if_not_exists()
            
            # 准备批量操作
            actions = []
            for idx, chunk in enumerate(chunks):
                actions.append({
                    "index": {
                        "_index": self.index_name
                    }
                })
                actions.append({
                    "content": chunk,
                    "document_id": document_id,
                    "chunk_id": idx,
                    "created_at": self._get_timestamp()
                })
            
            # 执行批量索引
            from elasticsearch.helpers import bulk
            success, failed = bulk(
                self.es_client,
                actions,
                stats_only=True
            )
            
            print(f"✅ ES 批量索引: 成功 {success} 条")
            return success
        except Exception as e:
            print(f"❌ 批量索引失败: {str(e)}")
            return 0
    
    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        关键词搜索（BM25）
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        if not self.enabled:
            return []
        
        try:
            # BM25 搜索
            search_body = {
                "query": {
                    "match": {
                        "content": {
                            "query": query,
                            "operator": "or"
                        }
                    }
                },
                "size": top_k,
                "_source": ["content", "document_id", "chunk_id"]
            }
            
            response = self.es_client.search(
                index=self.index_name,
                body=search_body
            )
            
            # 格式化结果
            results = []
            for hit in response['hits']['hits']:
                results.append({
                    "content": hit['_source']['content'],
                    "score": hit['_score'],
                    "document_id": hit['_source'].get('document_id'),
                    "chunk_id": hit['_source'].get('chunk_id')
                })
            
            return results
        except Exception as e:
            print(f"❌ ES 搜索失败: {str(e)}")
            return []
    
    def delete_by_document_id(self, document_id: int) -> int:
        """
        删除指定文档的所有块
        
        Args:
            document_id: 文档ID
        
        Returns:
            删除的数量
        """
        if not self.enabled:
            return 0
        
        try:
            query = {
                "query": {
                    "term": {
                        "document_id": document_id
                    }
                }
            }
            
            response = self.es_client.delete_by_query(
                index=self.index_name,
                body=query
            )
            
            deleted = response.get('deleted', 0)
            print(f"✅ 删除 ES 文档: {deleted} 条")
            return deleted
        except Exception as e:
            print(f"❌ 删除文档失败: {str(e)}")
            return 0
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        获取索引统计信息
        
        Returns:
            统计信息
        """
        if not self.enabled:
            return {
                "enabled": False,
                "message": "Elasticsearch 未启用"
            }
        
        try:
            stats = self.es_client.indices.stats(index=self.index_name)
            count = self.es_client.count(index=self.index_name)
            
            return {
                "enabled": True,
                "index_name": self.index_name,
                "document_count": count['count'],
                "size": stats['_all']['total']['store']['size_in_bytes'],
                "size_human": self._format_bytes(stats['_all']['total']['store']['size_in_bytes'])
            }
        except Exception as e:
            return {
                "enabled": False,
                "error": str(e)
            }
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _format_bytes(self, bytes_size: int) -> str:
        """格式化字节大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"

# 创建全局实例
es_service = ElasticsearchService()
