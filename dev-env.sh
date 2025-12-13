#!/bin/bash

# ===================== 配置项（可根据实际修改） =====================
# Docker Compose 配置文件路径
COMPOSE_FILE="./docker-compose.yml"
# 自定义网络名称（和 compose 配置中一致）
NETWORK_NAME="my-rag-learning_rag-network"
# Minio 控制台访问地址（根据你修改后的端口调整）
MINIO_CONSOLE="http://localhost:9003"
# Redis 连接命令
REDIS_CHECK_CMD="docker exec -it redis-rag redis-cli -a 123456 ping"

# ===================== 颜色常量（美化输出） =====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # 重置颜色

# ===================== 前置检查函数 =====================
check_prerequisite() {
    # 检查 Docker 是否运行
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}[错误] Docker 未运行，请先启动 Docker！${NC}"
        exit 1
    fi

    # 检查 Docker Compose 是否安装
    if ! docker compose version >/dev/null 2>&1; then
        echo -e "${RED}[错误] Docker Compose 未安装，请先安装！${NC}"
        exit 1
    fi

    # 检查 docker-compose.yml 是否存在
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}[错误] 配置文件 $COMPOSE_FILE 不存在，请先创建！${NC}"
        exit 1
    fi
}

# ===================== 核心功能函数 =====================
# 启动环境
start_env() {
    echo -e "${YELLOW}[提示] 正在启动 Redis+Minio 开发环境...${NC}"
    # 启动服务（后台运行）
    docker compose -f "$COMPOSE_FILE" up -d
    
    # 检查启动结果
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[成功] 环境启动完成！${NC}"
        echo -e "${YELLOW}[提示] Redis 地址：localhost:6379（密码：123456）${NC}"
        echo -e "${YELLOW}[提示] Minio 控制台：$MINIO_CONSOLE（账号：miniorag，密码：minio123456）${NC}"
        
        # 验证 Redis 连接（可选）
        echo -e "${YELLOW}[提示] 验证 Redis 连接...${NC}"
        sleep 2 # 等待 Redis 完全启动
        if $REDIS_CHECK_CMD | grep -q "PONG"; then
            echo -e "${GREEN}[成功] Redis 连接正常！${NC}"
        else
            echo -e "${YELLOW}[警告] Redis 可能未就绪，请稍后手动验证！${NC}"
        fi
    else
        echo -e "${RED}[错误] 环境启动失败，请查看日志：docker compose logs${NC}"
        exit 1
    fi
}

# 停止环境
stop_env() {
    echo -e "${YELLOW}[提示] 正在停止 Redis+Minio 开发环境...${NC}"
    docker compose -f "$COMPOSE_FILE" down
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[成功] 环境已停止！${NC}"
    else
        echo -e "${RED}[错误] 环境停止失败！${NC}"
        exit 1
    fi
}

# 查看环境状态
status_env() {
    echo -e "${YELLOW}[提示] 当前环境状态：${NC}"
    docker compose -f "$COMPOSE_FILE" ps
}

# 重启环境
restart_env() {
    echo -e "${YELLOW}[提示] 正在重启 Redis+Minio 开发环境...${NC}"
    stop_env
    sleep 1
    start_env
}

# ===================== 脚本入口（参数解析） =====================
main() {
    # 先执行前置检查
    check_prerequisite

    # 根据传入的参数执行对应功能
    case "$1" in
        start)
            start_env
            ;;
        stop)
            stop_env
            ;;
        status)
            status_env
            ;;
        restart)
            restart_env
            ;;
        *)
            # 无参数/参数错误时，输出帮助信息
            echo -e "${YELLOW}[使用说明]${NC}"
            echo "  $0 start    - 启动 Redis+Minio 开发环境"
            echo "  $0 stop     - 停止 Redis+Minio 开发环境"
            echo "  $0 status   - 查看环境运行状态"
            echo "  $0 restart  - 重启 Redis+Minio 开发环境"
            exit 1
            ;;
    esac
}

# 执行主函数（传入脚本第一个参数）
main "$1"

