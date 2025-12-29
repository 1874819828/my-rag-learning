# 🚀 快速开始指南

5 分钟快速部署并使用 RAG 问答系统！

## 📋 前置要求

- ✅ Docker 20.10+
- ✅ Docker Compose 2.0+
- ✅ 智谱 AI API Key ([获取地址](https://open.bigmodel.cn/))

## 🎯 三步部署

### 步骤 1：配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
# ZHIPU_API_KEY=your_api_key_here
```

### 步骤 2：启动服务

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```bash
deploy.bat
```

**或使用 Docker Compose:**
```bash
docker-compose up -d --build
```

### 步骤 3：验证部署

```bash
# 查看服务状态
docker-compose ps

# 运行测试脚本
python test_deployment.py
```

## 🎮 开始使用

### 1. 访问 API 文档

打开浏览器访问：http://localhost:8000/docs

### 2. 上传文档

在 Swagger UI 中找到 `/api/upload` 接口：

1. 点击 "Try it out"
2. 选择一个 `.txt` 或 `.pdf` 文件
3. 点击 "Execute"
4. 等待上传完成

**示例文档内容** (test.txt):
```
Python 是一种高级编程语言。
它由 Guido van Rossum 于 1991 年创建。
Python 以其简洁的语法和强大的功能而闻名。
```

### 3. 开始问答

在 Swagger UI 中找到 `/api/chat` 接口：

1. 点击 "Try it out"
2. 输入问题，例如：
```json
{
  "question": "Python 是什么时候创建的？"
}
```
3. 点击 "Execute"
4. 查看 AI 回答

**预期响应:**
```json
{
  "answer": "Python 由 Guido van Rossum 于 1991 年创建。",
  "session_id": "xxx-xxx-xxx",
  "message_id": 1
}
```

### 4. 查看会话历史

使用 `/api/conversation/list` 接口查看所有会话。

## 📊 使用示例

### 示例 1：技术文档问答

**上传文档:** `fastapi_intro.txt`
```
FastAPI 是一个现代、快速的 Web 框架。
它基于 Python 3.6+ 类型提示。
FastAPI 支持自动生成 API 文档。
```

**提问:**
- "FastAPI 是什么？"
- "FastAPI 有什么特点？"
- "FastAPI 支持哪些功能？"

### 示例 2：产品说明问答

**上传文档:** `product_manual.txt`
```
本产品是一款智能音箱。
支持语音控制和音乐播放。
电池续航时间为 8 小时。
```

**提问:**
- "这个产品的续航时间是多久？"
- "产品有哪些功能？"

### 示例 3：多轮对话

```json
// 第一轮
{
  "question": "Python 是什么？"
}

// 第二轮（使用相同 session_id）
{
  "question": "它是谁创建的？",
  "session_id": "上一轮返回的 session_id"
}
```

## 🔧 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f fastapi-app

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 使用 Makefile（推荐）
make up          # 启动
make logs        # 查看日志
make down        # 停止
make help        # 查看所有命令
```

## 🎨 可视化工具

### Attu (Milvus Web UI)

启动 Attu 查看向量数据：

```bash
docker-compose --profile tools up -d attu
```

访问：http://localhost:8001

连接信息：
- Milvus Address: `milvus-standalone:19530`

### Python 脚本查看数据

```bash
python view_milvus.py
```

## 🐛 常见问题

### Q1: 服务启动失败

```bash
# 查看详细日志
docker-compose logs fastapi-app

# 检查端口占用
netstat -tuln | grep 8000

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

### Q2: 无法连接数据库

```bash
# 检查 MySQL 状态
docker-compose ps mysql

# 查看 MySQL 日志
docker-compose logs mysql

# 重启 MySQL
docker-compose restart mysql
```

### Q3: 向量检索失败

```bash
# 检查 Milvus 状态
docker-compose ps milvus-standalone

# 查看 Milvus 日志
docker-compose logs milvus-standalone

# 重启 Milvus
docker-compose restart milvus-standalone
```

### Q4: API Key 错误

确保 `.env` 文件中的 `ZHIPU_API_KEY` 正确：

```bash
# 查看当前配置
cat .env | grep ZHIPU_API_KEY

# 重新启动服务使配置生效
docker-compose restart fastapi-app
```

## 📚 下一步

- 📖 阅读 [完整文档](README.md)
- 🚀 查看 [部署指南](DEPLOYMENT.md)
- 🔧 了解 [API 接口](http://localhost:8000/docs)
- 🎯 尝试更多功能

## 🆘 获取帮助

遇到问题？

1. 查看 [故障排查](DEPLOYMENT.md#故障排查)
2. 运行测试脚本: `python test_deployment.py`
3. 查看日志: `docker-compose logs -f`
4. 提交 Issue

---

**祝你使用愉快！🎉**
