# RAG 系统容器化部署指南

## 📋 目录

- [快速开始](#快速开始)
- [系统架构](#系统架构)
- [部署方式](#部署方式)
- [配置说明](#配置说明)
- [常用命令](#常用命令)
- [故障排查](#故障排查)
- [生产环境部署](#生产环境部署)

## 🚀 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

### 一键部署

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
# 编辑 .env 文件，填入你的 ZHIPU_API_KEY

# 2. 启动所有服务
docker-compose up -d --build

# 3. 查看服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f
```

### 访问服务

部署完成后，访问以下地址：

- **FastAPI 文档**: http://localhost:8000/docs
- **FastAPI API**: http://localhost:8000
- **Attu (Milvus UI)**: http://localhost:8001 (可选)

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                     (rag-network)                        │
│                                                          │
│  ┌──────────────┐      ┌──────────────┐                │
│  │  FastAPI App │◄────►│    MySQL     │                │
│  │  (Port 8000) │      │  (Port 3306) │                │
│  └──────┬───────┘      └──────────────┘                │
│         │                                                │
│         │              ┌──────────────┐                │
│         ├─────────────►│    Milvus    │                │
│         │              │ (Port 19530) │                │
│         │              └──────┬───────┘                │
│         │                     │                         │
│         │              ┌──────┴───────┐                │
│         │              │  etcd/minio  │                │
│         │              └──────────────┘                │
│         │                                                │
│         │              ┌──────────────┐                │
│         └─────────────►│    Redis     │                │
│                        │  (Port 6379) │                │
│                        └──────────────┘                │
│                                                          │
│  ┌──────────────┐                                       │
│  │     Attu     │  (可选)                              │
│  │  (Port 8001) │                                       │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘
```

### 服务说明

| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| FastAPI | rag-fastapi | 8000 | RAG 应用主服务 |
| MySQL | mysql-rag | 3306 | 关系数据库（会话/消息/文档） |
| Milvus | milvus-standalone | 19530 | 向量数据库 |
| Redis | rag-redis | 6379 | 缓存/会话存储 |
| etcd | milvus-etcd | 2379 | Milvus 元数据存储 |
| MinIO | milvus-minio | 9000 | Milvus 对象存储 |
| Attu | milvus-attu | 8001 | Milvus Web UI（可选） |

## 🔧 部署方式

### 方式 1：完整部署（推荐）

启动所有服务，包括 Attu：

```bash
docker-compose --profile tools up -d --build
```

### 方式 2：核心服务部署

只启动核心服务，不包括 Attu：

```bash
docker-compose up -d --build
```

### 方式 3：开发模式

启动服务并实时查看日志：

```bash
docker-compose up --build
```

## ⚙️ 配置说明

### 环境变量配置

创建 `.env` 文件：

```env
# ==================== 必填配置 ====================
# 智谱 AI API Key（必须）
ZHIPU_API_KEY=your_api_key_here

# ==================== 可选配置 ====================
# MySQL 配置
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root123
MYSQL_DATABASE=rag_db

# Milvus 配置
MILVUS_HOST=milvus-standalone
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=doc_rag_collection
VECTOR_DIM=384
TOP_K=3

# Redis 配置
REDIS_HOST=redis
REDIS_PORT=6379

# 文件上传配置
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=10485760  # 10MB
```

### 数据持久化

所有数据存储在 `volumes/` 目录：

```
volumes/
├── mysql/      # MySQL 数据
├── milvus/     # Milvus 向量数据
├── redis/      # Redis 数据
├── etcd/       # etcd 元数据
└── minio/      # MinIO 对象存储
```

### 端口映射

如需修改端口，编辑 `docker-compose.yml`：

```yaml
services:
  fastapi-app:
    ports:
      - "8080:8000"  # 修改为 8080
```

## 📝 常用命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重启单个服务
docker-compose restart fastapi-app

# 停止并删除所有数据
docker-compose down -v
```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f fastapi-app
docker-compose logs -f mysql
docker-compose logs -f milvus-standalone

# 查看最近 100 行日志
docker-compose logs --tail=100 fastapi-app
```

### 服务状态

```bash
# 查看服务状态
docker-compose ps

# 查看资源使用
docker stats

# 进入容器
docker exec -it rag-fastapi bash
docker exec -it mysql-rag mysql -uroot -proot123
```

### 数据管理

```bash
# 备份 MySQL 数据
docker exec mysql-rag mysqldump -uroot -proot123 rag_db > backup.sql

# 恢复 MySQL 数据
docker exec -i mysql-rag mysql -uroot -proot123 rag_db < backup.sql

# 清理未使用的镜像和容器
docker system prune -a
```

## 🔍 故障排查

### 问题 1：服务启动失败

**症状**: 容器无法启动或立即退出

**解决方法**:
```bash
# 查看详细日志
docker-compose logs fastapi-app

# 检查端口占用
netstat -tuln | grep 8000

# 重新构建镜像
docker-compose build --no-cache fastapi-app
docker-compose up -d
```

### 问题 2：MySQL 连接失败

**症状**: FastAPI 无法连接 MySQL

**解决方法**:
```bash
# 检查 MySQL 健康状态
docker-compose ps mysql

# 查看 MySQL 日志
docker-compose logs mysql

# 手动测试连接
docker exec -it mysql-rag mysql -uroot -proot123 -e "SHOW DATABASES;"
```

### 问题 3：Milvus 连接失败

**症状**: 向量检索失败

**解决方法**:
```bash
# 检查 Milvus 状态
docker-compose ps milvus-standalone

# 查看 Milvus 日志
docker-compose logs milvus-standalone

# 检查依赖服务
docker-compose ps etcd minio
```

### 问题 4：内存不足

**症状**: 容器频繁重启或 OOM

**解决方法**:
```bash
# 限制服务内存使用（编辑 docker-compose.yml）
services:
  fastapi-app:
    deploy:
      resources:
        limits:
          memory: 1G
```

### 问题 5：磁盘空间不足

**解决方法**:
```bash
# 清理未使用的资源
docker system prune -a --volumes

# 查看磁盘使用
docker system df
```

## 🌐 生产环境部署

### 安全加固

1. **修改默认密码**

编辑 `docker-compose.yml`：
```yaml
environment:
  MYSQL_ROOT_PASSWORD: your_strong_password
  MYSQL_PASSWORD: your_strong_password
```

2. **使用 HTTPS**

配置 Nginx 反向代理：
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **限制网络访问**

修改端口映射，只暴露必要端口：
```yaml
ports:
  - "127.0.0.1:8000:8000"  # 只允许本地访问
```

### 性能优化

1. **使用生产级 WSGI 服务器**

修改 `run.py`：
```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # 多进程
        reload=False
    )
```

2. **配置资源限制**

```yaml
services:
  fastapi-app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

3. **启用 Redis 缓存**

在应用中集成 Redis 缓存热门查询结果。

### 监控和日志

1. **集成日志收集**

使用 ELK Stack 或 Loki 收集日志。

2. **添加健康检查**

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

3. **配置告警**

使用 Prometheus + Grafana 监控服务状态。

### 云服务器部署

**阿里云/腾讯云/AWS:**

```bash
# 1. 安装 Docker
curl -fsSL https://get.docker.com | sh

# 2. 克隆项目
git clone your-repo-url
cd your-project

# 3. 配置环境变量
vim .env

# 4. 启动服务
./deploy.sh

# 5. 配置防火墙
# 开放端口: 8000, 8001 (可选)
```

## 📚 参考资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)
- [Milvus 部署文档](https://milvus.io/docs/install_standalone-docker.md)

## 🆘 获取帮助

遇到问题？

1. 查看日志: `docker-compose logs -f`
2. 检查服务状态: `docker-compose ps`
3. 查看本文档的故障排查部分
4. 提交 Issue 到项目仓库

---

**祝你部署顺利！🎉**
