# Elasticsearch 快速启动指南

## ✅ 前提条件

在启动 Elasticsearch 之前，请确保：

1. **Docker 代理已禁用或正常工作**
   - 打开 Docker Desktop → Settings → Resources → Proxies
   - 取消勾选 "Manual proxy configuration"
   - 或确保代理服务正在运行

2. **已拉取 Elasticsearch 镜像**
   ```bash
   docker pull elasticsearch:8.11.0
   ```

3. **docker-compose.yml 配置正确**
   - 使用命名卷而不是绑定挂载（避免 WSL 权限问题）
   - 已配置环境变量

---

## 🚀 快速启动

### 方法 1：使用 Docker Compose（推荐）

```bash
# 启动所有服务（包括 Elasticsearch）
docker-compose up -d

# 或只启动 Elasticsearch
docker-compose up -d elasticsearch

# 查看日志
docker-compose logs -f elasticsearch

# 检查状态
docker-compose ps
```

### 方法 2：手动启动

```bash
docker run -d \
  --name rag-elasticsearch \
  --network rag-network \
  --user 1000:1000 \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  -e "bootstrap.memory_lock=true" \
  --ulimit memlock=-1:-1 \
  -v es-data:/usr/share/elasticsearch/data \
  elasticsearch:8.11.0
```

---

## ✅ 验证启动

### 1. 检查容器状态
```bash
docker ps | grep elasticsearch
# 应该显示：Up X minutes (healthy)
```

### 2. 检查集群健康
```bash
curl http://localhost:9200/_cluster/health
# 应该返回 JSON，status 为 "green" 或 "yellow"
```

### 3. 获取集群信息
```bash
curl http://localhost:9200
# 应该返回版本信息等
```

### 4. 检查 FastAPI 连接
```bash
# 重启 FastAPI 以连接 ES
docker restart rag-fastapi

# 查看日志
docker logs rag-fastapi --tail 20
# 应该显示：✅ Elasticsearch 服务已启用 (版本: 8.11.0)
```

---

## 🧪 测试混合检索

### 1. 上传测试文档
```bash
# 使用 FastAPI 接口上传文档
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@test.txt"
```

### 2. 运行测试脚本
```bash
python scripts/test_hybrid_search.py
```

### 3. 查看索引
```bash
# 查看所有索引
curl http://localhost:9200/_cat/indices

# 查看 rag_documents 索引
curl http://localhost:9200/rag_documents/_search?pretty
```

---

## ⚠️ 常见问题

### 问题 1：容器启动后立即退出

**查看日志：**
```bash
docker logs rag-elasticsearch
```

**可能原因：**
- 权限问题（使用命名卷解决）
- 内存不足（调整 ES_JAVA_OPTS）
- 端口被占用

**解决方法：**
```bash
# 检查端口占用
netstat -ano | findstr "9200"

# 完全重置
docker-compose down
docker volume rm my_rag_es-data
docker-compose up -d
```

### 问题 2：FastAPI 无法连接 ES

**症状：**
```
⚠️  Elasticsearch 连接失败
```

**解决方法：**
```bash
# 1. 检查 ES 是否运行
docker ps | grep elasticsearch

# 2. 检查网络连接
docker exec rag-fastapi curl http://elasticsearch:9200

# 3. 检查环境变量
docker exec rag-fastapi env | grep ES_

# 4. 重启 FastAPI
docker restart rag-fastapi
```

### 问题 3：版本不兼容错误

**症状：**
```
BadRequestError: Accept version must be either version 8 or 7, but found 9
```

**解决方法：**
```bash
# 确保 requirements.txt 中版本正确
# elasticsearch>=8.11.0,<8.12.0

# 重新构建镜像
docker-compose build fastapi-app
docker-compose up -d fastapi-app
```

---

## 📊 服务状态检查

### 完整的服务检查命令

```bash
# 1. 检查所有容器
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 2. 检查 ES 健康
curl http://localhost:9200/_cluster/health?pretty

# 3. 检查 FastAPI 日志
docker logs rag-fastapi --tail 20

# 4. 检查 ES 日志
docker logs rag-elasticsearch --tail 50

# 5. 运行诊断脚本
python scripts/diagnose_es.py
```

---

## 🎯 下一步

Elasticsearch 启动成功后：

1. **上传文档** - 文档会自动索引到 Milvus 和 ES
2. **测试检索** - 使用混合检索 API 测试效果
3. **调整权重** - 在 `.env` 中调整 `VECTOR_WEIGHT` 和 `KEYWORD_WEIGHT`
4. **监控性能** - 观察检索质量和响应时间

---

## 📚 详细文档

遇到问题？查看完整的故障排查指南：

- [完整故障排查指南](docs/ES_TROUBLESHOOTING.md) - 所有问题的详细解决方案
- [Stage 6.2 文档](docs/STAGE6.2_ELASTICSEARCH.md) - Elasticsearch 集成说明
- [部署指南](docs/DEPLOYMENT.md) - 生产环境部署

---

## 💡 提示

- Elasticsearch 首次启动需要 30-60 秒
- 确保至少有 1GB 可用内存
- 在 WSL 环境下必须使用命名卷
- 客户端版本必须与服务器版本兼容

---

**🎉 启动成功！现在你的 RAG 系统支持混合检索了！**
