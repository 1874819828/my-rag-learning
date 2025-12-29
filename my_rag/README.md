# RAG问答系统

基于FastAPI、Milvus、MySQL和智谱AI的检索增强生成（RAG）系统。

## 项目结构

```
my_rag/
├── app/                  # 应用代码
│   ├── api/              # API路由层
│   ├── models/           # 数据模型层
│   ├── services/         # 业务逻辑层
│   ├── config.py         # 配置文件
│   ├── database.py       # 数据库连接
│   └── main.py           # FastAPI应用入口
├── docs/                 # 文档目录
│   ├── DEPLOYMENT.md     # 部署指南
│   ├── QUICKSTART.md     # 快速开始
│   └── ...
├── scripts/              # 工具脚本
│   ├── test_deployment.py
│   ├── test_e2e.py
│   └── view_milvus.py
├── docker-compose.yml    # Docker服务编排
├── Dockerfile            # FastAPI镜像
├── requirements.txt      # Python依赖
└── README.md            # 项目说明
```

## 功能特性

### 阶段2：最小可行项目
- ✅ FastAPI三层架构（路由/服务/模型）
- ✅ 智谱AI API集成
- ✅ 问答接口（/api/chat）

### 阶段3：向量数据库检索
- ✅ Milvus向量数据库集成
- ✅ BGE向量模型（BAAI/bge-small-zh-v1.5）
- ✅ 文档切分与向量化
- ✅ 相似度检索

### 阶段4：传统数据库管理
- ✅ MySQL会话和消息存储
- ✅ 文档元信息管理
- ✅ 会话历史查询

## 快速开始

### 方式 1：Docker 一键部署（推荐）⭐

**前置要求：**
- Docker 20.10+
- Docker Compose 2.0+

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```bash
deploy.bat
```

**或手动部署:**
```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 ZHIPU_API_KEY

# 2. 一键启动所有服务
docker-compose up -d --build

# 3. 访问服务
# FastAPI: http://localhost:8000/docs
# Attu: http://localhost:8001 (可选)
```

**常用命令:**
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 使用 Makefile（推荐）
make up          # 启动服务
make logs        # 查看日志
make down        # 停止服务
make help        # 查看所有命令
```

### 方式 2：本地开发部署

**1. 环境准备**

确保已安装：
- Python 3.8+
- Docker & Docker Compose

**2. 启动基础服务**

```bash
# 只启动 Milvus 和 MySQL
docker-compose up -d mysql milvus-standalone etcd minio
```

**3. 安装 Python 依赖**

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

**4. 配置环境变量**

创建 `.env` 文件：

```env
# 智谱AI配置（必填）
ZHIPU_API_KEY=your_api_key_here

# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root123
MYSQL_DATABASE=rag_db

# Milvus配置
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

**5. 启动 FastAPI 应用**

```bash
# 使用 run.py
python run.py

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**6. 访问服务**

- FastAPI 文档: http://localhost:8000/docs
- FastAPI API: http://localhost:8000

## API接口说明

### 1. 问答接口

**POST** `/api/chat`

请求体：
```json
{
  "question": "你的问题",
  "session_id": "可选，会话ID"
}
```

响应：
```json
{
  "answer": "AI回答",
  "session_id": "会话ID",
  "message_id": 123
}
```

### 2. 文档上传接口

**POST** `/api/upload`

- 支持格式：`.txt`, `.pdf`, `.md`
- 最大文件大小：10MB
- 自动切分、向量化并索引到Milvus

### 3. 会话管理接口

- **GET** `/api/conversation/list` - 获取会话列表
- **GET** `/api/conversation/{session_id}` - 获取会话详情
- **DELETE** `/api/conversation/{session_id}` - 删除会话

## 使用流程

1. **上传文档**：通过 `/api/upload` 上传文档，系统会自动处理并索引
2. **开始问答**：通过 `/api/chat` 提问，系统会：
   - 将问题向量化
   - 在Milvus中检索相关文档片段
   - 将检索结果作为上下文发送给LLM
   - 保存问答记录到MySQL
3. **查看历史**：通过 `/api/conversation` 查看历史会话

## 常见问题

### 1. Milvus连接失败

检查Milvus服务是否启动：
```bash
docker-compose ps
docker logs milvus-standalone
```

### 2. MySQL连接失败

检查MySQL服务状态：
```bash
docker-compose ps mysql
docker logs mysql-rag
```

### 3. 向量模型下载慢

BGE模型首次运行会自动下载（约400MB），请耐心等待。

### 4. 智谱AI API调用失败

检查API Key是否正确，查看错误日志：
```bash
# 查看应用日志
tail -f logs/app.log  # 如果有日志文件
```

## 开发说明

### 代码结构

- **路由层** (`app/api/`)：处理HTTP请求，参数验证
- **服务层** (`app/services/`)：业务逻辑，外部服务调用
- **模型层** (`app/models/`)：数据模型定义

### 扩展功能

- 支持更多文档格式（Word、Excel等）
- 优化文档切分策略（按语义切分）
- 添加用户认证
- 支持多轮对话上下文

## 📦 容器化部署

### 系统架构

```
┌─────────────────────────────────────────┐
│         Docker Network (rag-network)    │
│                                          │
│  FastAPI ──► MySQL                      │
│     │        Redis                       │
│     └──────► Milvus (etcd + minio)      │
│              Attu (可选)                 │
└─────────────────────────────────────────┘
```

### 服务列表

| 服务 | 端口 | 说明 |
|------|------|------|
| FastAPI | 8000 | RAG 应用主服务 |
| MySQL | 3306 | 关系数据库 |
| Milvus | 19530 | 向量数据库 |
| Redis | 6379 | 缓存服务 |
| Attu | 8001 | Milvus Web UI（可选） |

### 详细部署文档

查看 [DEPLOYMENT.md](docs/DEPLOYMENT.md) 获取完整的部署指南，包括：
- 生产环境部署
- 安全加固
- 性能优化
- 故障排查
- 监控和日志

## 🔧 开发指南

### 项目结构

```
my_rag/
├── app/                    # 应用代码
│   ├── api/               # API 路由
│   ├── services/          # 业务逻辑
│   ├── models/            # 数据模型
│   ├── config.py          # 配置
│   └── main.py            # 入口
├── docker-compose.yml     # Docker 编排
├── Dockerfile             # Docker 镜像
├── requirements.txt       # Python 依赖
├── deploy.sh              # 部署脚本（Linux/Mac）
├── deploy.bat             # 部署脚本（Windows）
├── Makefile               # 常用命令
└── DEPLOYMENT.md          # 部署文档
```

### 添加新功能

1. 在 `app/api/` 添加新路由
2. 在 `app/services/` 添加业务逻辑
3. 在 `app/models/` 添加数据模型
4. 更新 API 文档

### 运行测试

```bash
# Docker 环境
make test

# 本地环境
pytest tests/
```

## 许可证

MIT License

