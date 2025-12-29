@echo off
REM RAG 系统一键部署脚本 (Windows)

echo ==========================================
echo   RAG 问答系统 - 一键部署
echo ==========================================
echo.

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: Docker 未安装
    echo 请先安装 Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM 检查 .env 文件
if not exist .env (
    echo ⚠️  警告: .env 文件不存在，创建默认配置...
    (
        echo # 智谱 AI 配置
        echo ZHIPU_API_KEY=your_api_key_here
        echo.
        echo # MySQL 配置（可选，使用默认值）
        echo MYSQL_HOST=mysql
        echo MYSQL_PORT=3306
        echo MYSQL_USER=root
        echo MYSQL_PASSWORD=root123
        echo MYSQL_DATABASE=rag_db
        echo.
        echo # Milvus 配置（可选，使用默认值）
        echo MILVUS_HOST=milvus-standalone
        echo MILVUS_PORT=19530
        echo.
        echo # Redis 配置（可选，使用默认值）
        echo REDIS_HOST=redis
        echo REDIS_PORT=6379
    ) > .env
    echo ✅ 已创建 .env 文件，请编辑并填入你的 ZHIPU_API_KEY
    echo.
)

REM 创建必要的目录
echo 📁 创建数据目录...
if not exist volumes\mysql mkdir volumes\mysql
if not exist volumes\milvus mkdir volumes\milvus
if not exist volumes\etcd mkdir volumes\etcd
if not exist volumes\minio mkdir volumes\minio
if not exist volumes\redis mkdir volumes\redis
if not exist uploads mkdir uploads
echo ✅ 目录创建完成
echo.

REM 停止旧容器
echo 🛑 停止旧容器...
docker-compose down 2>nul
echo.

REM 启动服务
echo 🚀 启动服务...
echo.

set /p ATTU="是否启动 Attu (Milvus Web UI)? [y/N]: "
if /i "%ATTU%"=="y" (
    echo 启动完整服务（包含 Attu）...
    docker-compose --profile tools up -d --build
) else (
    echo 启动核心服务（不含 Attu）...
    docker-compose up -d --build
)

echo.
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo.
echo ==========================================
echo   服务状态
echo ==========================================
docker-compose ps

echo.
echo ==========================================
echo   部署完成！
echo ==========================================
echo.
echo 📌 访问地址：
echo   - FastAPI 文档: http://localhost:8000/docs
echo   - FastAPI 根路径: http://localhost:8000
if /i "%ATTU%"=="y" (
    echo   - Attu (Milvus UI^): http://localhost:8001
)
echo.
echo 📌 服务端口：
echo   - FastAPI: 8000
echo   - MySQL: 3306
echo   - Milvus: 19530
echo   - Redis: 6379
echo.
echo 📌 常用命令：
echo   - 查看日志: docker-compose logs -f
echo   - 查看 FastAPI 日志: docker-compose logs -f fastapi-app
echo   - 停止服务: docker-compose down
echo   - 重启服务: docker-compose restart
echo.
echo 🎉 开始使用你的 RAG 系统吧！
echo.
pause
