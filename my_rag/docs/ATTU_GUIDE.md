# Attu - Milvus Web UI 使用指南

## 什么是 Attu？

Attu 是 Milvus 官方提供的 Web 管理界面，可以通过浏览器可视化地查看和管理 Milvus 向量数据库。

## ✅ 当前状态

Attu 已成功启动并运行在：
- **访问地址：** http://localhost:8001
- **容器名称：** milvus-attu
- **状态：** ✅ 运行中

---

## 🚀 启动 Attu

### 方法 1：使用 docker-compose（推荐）⭐

Attu 被配置为可选服务（profile: tools），需要使用特殊参数启动：

```bash
# 启动 Attu
docker-compose --profile tools up -d attu

# 检查状态
docker ps | grep attu

# 查看日志
docker logs milvus-attu
```

### 方法 2：启动所有服务（包括 Attu）

```bash
# 一次性启动所有服务，包括可选工具
docker-compose --profile tools up -d
```

### 方法 3：手动启动

```bash
docker run -d \
  --name milvus-attu \
  --network rag-network \
  -p 8001:3000 \
  -e MILVUS_URL=milvus-standalone:19530 \
  zilliz/attu:latest
```

---

## 🌐 访问 Attu

### 1. 打开浏览器

访问：**http://localhost:8001**

### 2. 连接 Milvus

在 Attu 登录页面输入：
- **Milvus Address**: `milvus-standalone:19530`
- 如果上面不行，尝试: `localhost:19530`

点击 "Connect" 即可连接。

### 3. 开始使用

连接成功后，你将看到 Milvus 的管理界面。

---

## 📊 Attu 功能介绍

### 1. 集合管理（Collections）
- ✅ 查看所有集合列表
- ✅ 查看集合详细信息（向量维度、数据条数等）
- ✅ 创建/删除集合
- ✅ 查看集合 Schema

**示例：** 你应该能看到 `doc_rag_collection` 集合

### 2. 数据浏览（Data）
- ✅ 浏览集合中的向量数据
- ✅ 查看每条数据的字段内容
  - `id`: 文档 ID
  - `chunk_id`: 分块 ID
  - `content`: 文本内容
  - `embedding`: 向量（384 维）
- ✅ 支持分页浏览
- ✅ 数据过滤和搜索

### 3. 向量搜索（Search）
- ✅ 可视化执行向量相似度搜索
- ✅ 输入查询向量，查看搜索结果
- ✅ 调整搜索参数
  - Top K（返回结果数量）
  - 相似度算法（L2、IP、COSINE）
  - 搜索表达式

### 4. 索引管理（Index）
- ✅ 查看集合的索引类型
- ✅ 查看索引参数
- ✅ 创建/删除索引
- ✅ 索引性能统计

**当前索引：** IVF_FLAT（倒排文件索引）

### 5. 统计信息（Overview）
- ✅ 查看集合的统计数据
- ✅ 数据条数
- ✅ 向量维度
- ✅ 索引状态
- ✅ 内存使用情况

### 6. 查询控制台（Query）
- ✅ 执行自定义查询
- ✅ 使用表达式过滤
- ✅ 查看查询结果

---

## 🎯 使用场景

### 场景 1：查看上传的文档

1. 点击左侧 "Collections"
2. 选择 `doc_rag_collection`
3. 点击 "Data" 标签
4. 浏览所有文档分块

### 场景 2：测试向量搜索

1. 在集合页面点击 "Search"
2. 输入查询向量（或使用示例向量）
3. 设置 Top K = 3
4. 点击 "Search" 查看结果

### 场景 3：监控数据库状态

1. 点击 "Overview"
2. 查看集合统计信息
3. 检查索引状态
4. 监控数据增长

### 场景 4：调试检索问题

1. 使用 "Query" 功能执行自定义查询
2. 查看返回的向量和相似度分数
3. 对比不同查询参数的效果

---

## 🔧 常见问题

### Q1: 无法访问 http://localhost:8001

**检查容器状态：**
```bash
docker ps | grep attu
# 应该显示 "Up" 状态
```

**查看日志：**
```bash
docker logs milvus-attu
# 应该显示 "Attu server started"
```

**重启容器：**
```bash
docker restart milvus-attu
```

### Q2: 无法连接到 Milvus

**症状：** 在 Attu 登录页面连接失败

**解决方法：**
1. 确保 Milvus 容器正在运行
   ```bash
   docker ps | grep milvus-standalone
   ```

2. 使用正确的地址
   - ✅ 推荐：`milvus-standalone:19530`
   - ⚠️ 备选：`localhost:19530`

3. 检查网络连接
   ```bash
   docker exec milvus-attu ping milvus-standalone
   ```

### Q3: Attu 容器启动失败

**查看详细日志：**
```bash
docker logs milvus-attu --tail 50
```

**可能原因：**
- 端口 8001 被占用
- Milvus 服务未启动
- 网络配置问题

**解决方法：**
```bash
# 检查端口占用
netstat -ano | findstr "8001"

# 重新启动
docker-compose --profile tools down
docker-compose --profile tools up -d
```

### Q4: 看不到数据

**原因：** 可能还没有上传文档

**解决方法：**
```bash
# 上传测试文档
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@test.txt"

# 或使用 FastAPI 文档界面
# 访问 http://localhost:8000/docs
```

### Q5: 镜像拉取失败

**症状：**
```
Error response from daemon: Get "https://registry-1.docker.io/v2/": 
proxyconnect tcp: dial tcp 127.0.0.1:7890: connect: connection refused
```

**解决方法：**
1. 禁用 Docker Desktop 代理
   - Settings → Resources → Proxies
   - 取消勾选 "Manual proxy configuration"

2. 手动拉取镜像
   ```bash
   docker pull zilliz/attu:latest
   ```

---

## 🛑 停止 Attu

### 临时停止
```bash
docker stop milvus-attu
```

### 完全删除
```bash
docker stop milvus-attu
docker rm milvus-attu
```

### 使用 docker-compose
```bash
docker-compose --profile tools down
```

---

## 🔄 重启 Attu

```bash
# 方法 1：重启容器
docker restart milvus-attu

# 方法 2：停止后重新启动
docker-compose --profile tools down
docker-compose --profile tools up -d attu
```

---

## 📸 界面预览

### 登录页面
- 输入 Milvus 地址
- 点击 Connect

### 主界面
- **左侧导航栏：** Collections, System View
- **顶部标签：** Overview, Data, Search, Query, Index
- **主内容区：** 显示集合信息和数据

### 集合列表
- 显示所有集合
- 每个集合显示：
  - 名称
  - 数据条数
  - 向量维度
  - 索引类型

### 数据浏览
- 表格形式显示数据
- 每行一条记录
- 可以查看向量值
- 支持分页

---

## 🎓 学习资源

### Attu 官方文档
- GitHub: https://github.com/zilliztech/attu
- 使用指南: https://milvus.io/docs/attu.md

### Milvus 文档
- 官方网站: https://milvus.io
- 中文文档: https://milvus.io/cn/docs

---

## 🔀 其他 Milvus 管理工具

如果 Attu 无法使用，还可以尝试：

### 1. Milvus CLI（命令行工具）
```bash
pip install milvus-cli
milvus_cli
```

### 2. Python 脚本（项目自带）
```bash
python scripts/view_milvus.py
```

### 3. FastAPI 文档界面
访问：http://localhost:8000/docs
- 可以测试所有 API
- 查看文档列表
- 执行搜索

### 4. 直接使用 Python SDK
```python
from pymilvus import connections, Collection

# 连接
connections.connect(host="localhost", port="19530")

# 获取集合
collection = Collection("doc_rag_collection")

# 查询数据
results = collection.query(
    expr="id > 0",
    limit=10,
    output_fields=["id", "content"]
)
print(results)
```

---

## 💡 最佳实践

### 1. 定期检查数据
- 每次上传文档后，在 Attu 中验证
- 检查向量维度是否正确
- 确认数据完整性

### 2. 监控性能
- 观察查询响应时间
- 检查索引效率
- 监控内存使用

### 3. 调试检索
- 使用 Attu 的 Search 功能测试不同参数
- 对比不同 Top K 值的效果
- 验证相似度分数

### 4. 数据管理
- 定期清理无用数据
- 优化索引配置
- 备份重要集合

---

## 📊 Attu vs 其他工具对比

| 功能 | Attu | Milvus CLI | Python 脚本 | FastAPI Docs |
|------|------|-----------|------------|--------------|
| 可视化界面 | ✅ 优秀 | ❌ 命令行 | ❌ 命令行 | ✅ 一般 |
| 数据浏览 | ✅ 直观 | ⚠️ 文本 | ⚠️ 文本 | ❌ 不支持 |
| 向量搜索 | ✅ 可视化 | ✅ 支持 | ✅ 支持 | ✅ 支持 |
| 集合管理 | ✅ 完整 | ✅ 完整 | ⚠️ 有限 | ⚠️ 有限 |
| 易用性 | ✅ 最佳 | ⚠️ 需学习 | ⚠️ 需编码 | ✅ 简单 |
| 功能完整性 | ✅ 完整 | ✅ 完整 | ⚠️ 基础 | ⚠️ 基础 |

**推荐：** 日常使用 Attu，调试时结合 Python 脚本

---

## 🎯 快速验证清单

启动 Attu 后，请验证：

- [ ] 可以访问 http://localhost:8001
- [ ] 可以连接到 Milvus
- [ ] 可以看到 `doc_rag_collection` 集合
- [ ] 可以浏览数据（如果已上传文档）
- [ ] 可以执行向量搜索
- [ ] 可以查看集合统计信息

---

## 📝 总结

Attu 是管理 Milvus 最直观的工具，提供了：
- ✅ 可视化的数据浏览
- ✅ 强大的搜索功能
- ✅ 完整的集合管理
- ✅ 实时的性能监控

**强烈推荐使用 Attu 来管理和调试你的向量数据库！**

---

*最后更新：2024-12-30*
