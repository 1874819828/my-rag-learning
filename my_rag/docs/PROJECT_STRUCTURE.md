# 项目结构说明

## 📁 完整目录结构

```
my_rag/
│
├── 📂 app/                          # 应用代码
│   ├── 📂 api/                      # API 路由层
│   │   ├── __init__.py              # 路由注册
│   │   ├── chat.py                  # 问答接口
│   │   ├── upload.py                # 文档上传接口
│   │   └── conversation.py          # 会话管理接口
│   │
│   ├── 📂 services/                 # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── llm_service.py           # 智谱 AI 服务
│   │   ├── milvus_service.py        # Milvus 向量服务
│   │   ├── document_service.py      # 文档处理服务
│   │   └── conversation_service.py  # 会话管理服务
│   │
│   ├── 📂 models/                   # 数据模型层
│   │   ├── __init__.py
│   │   ├── database.py              # SQLAlchemy ORM 模型
│   │   └── schemas.py               # Pydantic 请求/响应模型
│   │
│   ├── __init__.py
│   ├── config.py                    # 配置管理
│   ├── database.py                  # 数据库连接
│   └── main.py                      # FastAPI 应用入口
│
├── 📂 volumes/                      # 数据持久化目录
│   ├── mysql/                       # MySQL 数据
│   ├── milvus/                      # Milvus 向量数据
│   ├── redis/                       # Redis 数据
│   ├── etcd/                        # etcd 元数据
│   └── minio/                       # MinIO 对象存储
│
├── 📂 uploads/                      # 上传文件存储
│
├── 📂 rag_venv/                     # Python 虚拟环境（可选）
│
├── 🐳 Docker 相关
│   ├── Dockerfile                   # FastAPI 应用镜像
│   ├── docker-compose.yml           # 服务编排配置
│   └── .dockerignore                # Docker 构建忽略
│
├── 🚀 部署脚本
│   ├── deploy.sh                    # Linux/Mac 部署脚本
│   ├── deploy.bat                   # Windows 部署脚本
│   └── Makefile                     # 常用命令快捷方式
│
├── ⚙️ 配置文件
│   ├── .env                         # 环境变量（不提交）
│   ├── .env.example                 # 环境变量模板
│   ├── requirements.txt             # Python 依赖
│   └── .gitignore                   # Git 忽略规则
│
├── 🧪 测试和工具
│   ├── test_deployment.py           # 部署验证脚本
│   ├── view_milvus.py               # Milvus 数据查看工具
│   └── start_attu.sh                # Attu 启动脚本
│
├── 📚 文档
│   ├── README.md                    # 项目总览
│   ├── QUICKSTART.md                # 快速开始指南
│   ├── DEPLOYMENT.md                # 完整部署指南
│   ├── STAGE5_SUMMARY.md            # 阶段 5 总结
│   ├── PROJECT_STRUCTURE.md         # 本文件
│   ├── ATTU_GUIDE.md                # Attu 使用指南
│   └── ATTU_FIX.md                  # Attu 问题修复
│
└── 🎯 应用入口
    └── run.py                       # FastAPI 启动脚本
```

## 📝 文件说明

### 核心应用代码

#### API 路由层 (`app/api/`)
- **chat.py**: 问答接口，处理用户提问，调用 LLM 生成回答
- **upload.py**: 文档上传接口，处理文件上传和索引
- **conversation.py**: 会话管理接口，查询和管理对话历史

#### 服务层 (`app/services/`)
- **llm_service.py**: 智谱 AI 集成，处理 LLM 调用
- **milvus_service.py**: Milvus 向量数据库操作，向量化和检索
- **document_service.py**: 文档处理，加载、切分、索引
- **conversation_service.py**: 会话管理，创建和查询会话

#### 模型层 (`app/models/`)
- **database.py**: SQLAlchemy ORM 模型（Conversation, Message, Document）
- **schemas.py**: Pydantic 数据模型（请求/响应验证）

#### 配置和入口
- **config.py**: 配置管理，环境变量读取
- **database.py**: 数据库连接和会话管理
- **main.py**: FastAPI 应用初始化和路由注册

### Docker 容器化

#### Dockerfile
定义 FastAPI 应用的 Docker 镜像：
- 基于 Python 3.10-slim
- 安装系统依赖和 Python 包
- 配置健康检查
- 暴露 8000 端口

#### docker-compose.yml
编排所有服务：
- FastAPI 应用
- MySQL 数据库
- Milvus 向量数据库
- Redis 缓存
- etcd、MinIO（Milvus 依赖）
- Attu Web UI（可选）

### 部署脚本

#### deploy.sh / deploy.bat
一键部署脚本，功能包括：
- 检查 Docker 环境
- 创建配置文件
- 创建数据目录
- 启动所有服务
- 显示访问地址

#### Makefile
常用命令快捷方式：
- `make up`: 启动服务
- `make down`: 停止服务
- `make logs`: 查看日志
- `make ps`: 查看状态
- `make clean`: 清理数据

### 配置文件

#### .env
环境变量配置（不提交到 Git）：
- 智谱 API Key
- 数据库连接信息
- 服务端口配置

#### requirements.txt
Python 依赖包：
- FastAPI、Uvicorn（Web 框架）
- SQLAlchemy、PyMySQL（数据库）
- pymilvus（向量数据库）
- sentence-transformers（向量模型）
- 其他工具库

### 测试和工具

#### test_deployment.py
部署验证脚本，测试：
- FastAPI 服务
- MySQL 连接
- Milvus 连接
- Redis 连接
- API 端点

#### view_milvus.py
Milvus 数据查看工具：
- 查看集合信息
- 浏览向量数据
- 替代 Attu 的命令行工具

### 文档

#### README.md
项目总览，包含：
- 项目介绍
- 功能特性
- 快速开始
- API 说明

#### QUICKSTART.md
5 分钟快速开始指南：
- 三步部署
- 使用示例
- 常见问题

#### DEPLOYMENT.md
完整部署指南：
- 系统架构
- 部署方式
- 配置说明
- 故障排查
- 生产环境建议

## 🔄 数据流

```
用户请求
    ↓
FastAPI (app/main.py)
    ↓
API 路由 (app/api/)
    ↓
服务层 (app/services/)
    ├─→ LLM Service → 智谱 AI
    ├─→ Milvus Service → Milvus
    └─→ Conversation Service → MySQL
    ↓
数据模型 (app/models/)
    ↓
响应返回
```

## 🎯 关键路径

### 文档上传流程
```
upload.py
  → document_service.py
    → 文件保存
    → 文档切分
    → milvus_service.py (向量化)
    → Milvus (存储向量)
    → MySQL (存储元信息)
```

### 问答流程
```
chat.py
  → conversation_service.py (获取/创建会话)
  → milvus_service.py (检索相关文档)
  → llm_service.py (生成回答)
  → conversation_service.py (保存消息)
  → MySQL (存储对话)
```

## 📊 技术栈

### 后端框架
- **FastAPI**: 现代 Python Web 框架
- **Uvicorn**: ASGI 服务器
- **Pydantic**: 数据验证

### 数据库
- **MySQL**: 关系数据库（会话、消息、文档）
- **Milvus**: 向量数据库（文档向量）
- **Redis**: 缓存服务

### AI 服务
- **智谱 AI**: LLM 服务（GLM-4）
- **BGE**: 向量模型（BAAI/bge-small-zh-v1.5）

### 容器化
- **Docker**: 容器化平台
- **Docker Compose**: 服务编排

## 🚀 扩展建议

### 添加新功能
1. 在 `app/api/` 创建新路由文件
2. 在 `app/services/` 实现业务逻辑
3. 在 `app/models/` 定义数据模型
4. 更新 API 文档

### 添加新服务
1. 在 `docker-compose.yml` 添加服务定义
2. 配置网络和依赖关系
3. 更新部署脚本
4. 更新文档

### 性能优化
1. 启用 Redis 缓存
2. 配置多进程 workers
3. 优化数据库查询
4. 添加 CDN

## 📚 参考资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Milvus 文档](https://milvus.io/docs)
- [Docker 文档](https://docs.docker.com/)
- [智谱 AI 文档](https://open.bigmodel.cn/dev/api)

---

**项目结构清晰，模块化设计，易于维护和扩展！**
