#!/bin/bash
# WSL 环境完整安装脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  RAG 系统 WSL 环境配置"
echo "=========================================="
echo ""

# 检查 Python
echo "1. 检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    echo "请运行: sudo apt update && sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"
echo ""

# 删除旧的虚拟环境
if [ -d "rag_venv" ]; then
    echo "2. 删除旧的虚拟环境..."
    rm -rf rag_venv
    echo "✅ 已删除"
else
    echo "2. 虚拟环境不存在，跳过删除"
fi
echo ""

# 创建新的虚拟环境
echo "3. 创建虚拟环境..."
python3 -m venv rag_venv
echo "✅ 虚拟环境创建完成"
echo ""

# 激活虚拟环境
echo "4. 激活虚拟环境..."
source rag_venv/bin/activate
echo "✅ 虚拟环境已激活"
echo ""

# 升级 pip
echo "5. 升级 pip..."
pip install --upgrade pip
echo "✅ pip 升级完成"
echo ""

# 安装依赖
echo "6. 安装项目依赖..."
echo "   这可能需要几分钟，请耐心等待..."
pip install -r requirements.txt
echo "✅ 依赖安装完成"
echo ""

# 验证安装
echo "7. 验证关键包..."
python3 -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)"
python3 -c "import uvicorn; print('✅ Uvicorn:', uvicorn.__version__)"
python3 -c "import pymilvus; print('✅ PyMilvus:', pymilvus.__version__)"
python3 -c "import redis; print('✅ Redis:', redis.__version__)"
echo ""

echo "=========================================="
echo "  安装完成！"
echo "=========================================="
echo ""
echo "📌 下一步："
echo "  1. 激活虚拟环境:"
echo "     source rag_venv/bin/activate"
echo ""
echo "  2. 启动服务:"
echo "     python3 run.py"
echo ""
echo "  或使用启动脚本:"
echo "     bash start_wsl.sh"
echo ""
