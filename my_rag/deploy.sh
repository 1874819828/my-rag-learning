#!/bin/bash
# RAG 系统一键部署脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  RAG 问答系统 - 一键部署"
echo "=========================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ 错误: Docker Compose 未安装"
    echo "请先安装 Docker Compose"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  警告: .env 文件不存在，创建默认配置..."
    cat > .env << EOF
# 智谱 AI 配置
ZHIPU_API_KEY=your_api_key_here

# MySQL 配置（可选，使用默认值）
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root123
MYSQL_DATABASE=rag_db

# Milvus 配置（可选，使用默认值）
MILVUS_HOST=milvus-standalone
MILVUS_PORT=19530

# Redis 配置（可选，使用默认值）
REDIS_HOST=redis
REDIS_PORT=6379
EOF
    echo "✅ 已创建 .env 文件，请编辑并填入你的 ZHIPU_API_KEY"
    echo ""
fi

# 创建必要的目录
echo "📁 创建数据目录..."
mkdir -p volumes/{mysql,milvus,etcd,minio,redis}
mkdir -p uploads
echo "✅ 目录创建完成"
echo ""

# 停止旧容器（如果存在）
echo "🛑 停止旧容器..."
docker-compose down 2>/dev/null || true
echo ""

# 构建并启动服务
echo "🚀 启动服务..."
echo ""

# 选择启动模式
read -p "是否启动 Attu (Milvus Web UI)? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "启动完整服务（包含 Attu）..."
    docker-compose --profile tools up -d --build
else
    echo "启动核心服务（不含 Attu）..."
    docker-compose up -d --build
fi

echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "=========================================="
echo "  服务状态"
echo "=========================================="
docker-compose ps

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "📌 访问地址："
echo "  - FastAPI 文档: http://localhost:8000/docs"
echo "  - FastAPI 根路径: http://localhost:8000"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  - Attu (Milvus UI): http://localhost:8001"
fi
echo ""
echo "📌 服务端口："
echo "  - FastAPI: 8000"
echo "  - MySQL: 3306"
echo "  - Milvus: 19530"
echo "  - Redis: 6379"
echo ""
echo "📌 常用命令："
echo "  - 查看日志: docker-compose logs -f"
echo "  - 查看 FastAPI 日志: docker-compose logs -f fastapi-app"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo ""
echo "🎉 开始使用你的 RAG 系统吧！"
