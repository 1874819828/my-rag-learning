.PHONY: help build up down restart logs ps clean test

# 默认目标
help:
	@echo "RAG 系统 - 常用命令"
	@echo ""
	@echo "部署相关:"
	@echo "  make build      - 构建 Docker 镜像"
	@echo "  make up         - 启动所有服务"
	@echo "  make up-full    - 启动所有服务（包含 Attu）"
	@echo "  make down       - 停止所有服务"
	@echo "  make restart    - 重启所有服务"
	@echo ""
	@echo "日志和监控:"
	@echo "  make logs       - 查看所有服务日志"
	@echo "  make logs-app   - 查看 FastAPI 日志"
	@echo "  make ps         - 查看服务状态"
	@echo ""
	@echo "数据管理:"
	@echo "  make clean      - 停止服务并删除数据卷"
	@echo "  make backup     - 备份 MySQL 数据"
	@echo "  make restore    - 恢复 MySQL 数据"
	@echo ""
	@echo "开发相关:"
	@echo "  make dev        - 开发模式启动（实时日志）"
	@echo "  make shell      - 进入 FastAPI 容器"
	@echo "  make test       - 运行测试"

# 构建镜像
build:
	docker-compose build

# 启动服务（核心）
up:
	docker-compose up -d
	@echo "✅ 服务已启动"
	@echo "访问: http://localhost:8000/docs"

# 启动服务（完整，包含 Attu）
up-full:
	docker-compose --profile tools up -d
	@echo "✅ 服务已启动（包含 Attu）"
	@echo "FastAPI: http://localhost:8000/docs"
	@echo "Attu: http://localhost:8001"

# 停止服务
down:
	docker-compose down
	@echo "✅ 服务已停止"

# 重启服务
restart:
	docker-compose restart
	@echo "✅ 服务已重启"

# 查看所有日志
logs:
	docker-compose logs -f

# 查看 FastAPI 日志
logs-app:
	docker-compose logs -f fastapi-app

# 查看服务状态
ps:
	docker-compose ps

# 清理所有数据
clean:
	docker-compose down -v
	@echo "⚠️  所有数据已删除"

# 备份 MySQL
backup:
	@mkdir -p backups
	docker exec mysql-rag mysqldump -uroot -proot123 rag_db > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ 备份完成: backups/backup_$$(date +%Y%m%d_%H%M%S).sql"

# 恢复 MySQL（需要指定文件: make restore FILE=backup.sql）
restore:
	@if [ -z "$(FILE)" ]; then \
		echo "❌ 请指定备份文件: make restore FILE=backup.sql"; \
		exit 1; \
	fi
	docker exec -i mysql-rag mysql -uroot -proot123 rag_db < $(FILE)
	@echo "✅ 数据已恢复"

# 开发模式
dev:
	docker-compose up --build

# 进入容器
shell:
	docker exec -it rag-fastapi bash

# 运行测试
test:
	docker exec rag-fastapi pytest tests/

# 查看资源使用
stats:
	docker stats --no-stream

# 清理 Docker 系统
prune:
	docker system prune -a
	@echo "✅ Docker 系统已清理"
