#!/bin/bash
# WSL 环境启动脚本

echo "=========================================="
echo "  RAG 系统启动 (WSL)"
echo "=========================================="
echo ""

# 检查虚拟环境
if [ ! -d "rag_venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv rag_venv
    echo "✅ 虚拟环境创建完成"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source rag_venv/bin/activate

# 检查依赖
echo "📋 检查依赖..."
pip list | grep -q fastapi
if [ $? -ne 0 ]; then
    echo "📦 安装依赖..."
    pip install -r requirements.txt
    echo "✅ 依赖安装完成"
fi

# 检查 Docker 服务
echo "🐳 检查 Docker 服务..."
docker ps > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Docker 正在运行"
    
    # 检查必要的容器
    if ! docker ps | grep -q "mysql-rag"; then
        echo "⚠️  MySQL 容器未运行，尝试启动..."
        docker start mysql-rag 2>/dev/null || echo "   请手动启动: docker-compose up -d"
    fi
    
    if ! docker ps | grep -q "milvus-standalone"; then
        echo "⚠️  Milvus 容器未运行，尝试启动..."
        docker start milvus-standalone 2>/dev/null || echo "   请手动启动: docker-compose up -d"
    fi
    
    if ! docker ps | grep -q "rag-redis"; then
        echo "⚠️  Redis 容器未运行，尝试启动..."
        docker start rag-redis 2>/dev/null || echo "   请手动启动: docker-compose up -d"
    fi
else
    echo "⚠️  Docker 未运行或无法访问"
    echo "   请确保 Docker Desktop 已启动"
fi

echo ""
echo "=========================================="
echo "  启动 FastAPI 服务"
echo "=========================================="
echo ""

# 启动服务
python3 run.py
