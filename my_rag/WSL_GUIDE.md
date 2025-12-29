# WSL 环境使用指南

## 🚀 快速开始

### 方法 1：使用安装脚本（推荐）

```bash
# 在 WSL 中，进入项目目录
cd ~/my-rag-learning/my_rag

# 给脚本执行权限
chmod +x setup_wsl.sh start_wsl.sh

# 运行安装脚本
bash setup_wsl.sh

# 启动服务
bash start_wsl.sh
```

### 方法 2：手动安装

```bash
# 1. 删除旧的虚拟环境
rm -rf rag_venv

# 2. 创建新的虚拟环境
python3 -m venv rag_venv

# 3. 激活虚拟环境
source rag_venv/bin/activate

# 4. 升级 pip
pip install --upgrade pip

# 5. 安装依赖
pip install -r requirements.txt

# 6. 启动服务
python3 run.py
```

## 📋 常用命令

### 虚拟环境管理

```bash
# 激活虚拟环境
source rag_venv/bin/activate

# 退出虚拟环境
deactivate

# 查看已安装的包
pip list

# 查看 Python 版本
python3 --version
```

### 启动服务

```bash
# 确保在项目目录
cd ~/my-rag-learning/my_rag

# 激活虚拟环境
source rag_venv/bin/activate

# 启动 FastAPI
python3 run.py
```

### 运行测试

```bash
# 激活虚拟环境
source rag_venv/bin/activate

# 缓存测试
python3 scripts/test_cache.py

# 混合检索测试
python3 scripts/test_hybrid_search.py

# Agent 测试
python3 scripts/test_agent.py

# 端到端测试
python3 scripts/test_e2e.py
```

## 🐳 Docker 管理

### 检查 Docker 状态

```bash
# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 查看容器日志
docker logs mysql-rag
docker logs milvus-standalone
docker logs rag-redis
```

### 启动/停止容器

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 启动特定服务
docker start mysql-rag
docker start milvus-standalone
docker start rag-redis

# 停止特定服务
docker stop mysql-rag
```

## ⚠️ 常见问题

### Q1: python 命令找不到

**问题：**
```bash
python run.py
# Command 'python' not found
```

**解决：**
在 WSL/Ubuntu 中使用 `python3` 而不是 `python`：
```bash
python3 run.py
```

或安装 python-is-python3：
```bash
sudo apt install python-is-python3
```

### Q2: 虚拟环境激活失败

**问题：**
```bash
source rag_venv/bin/activate
# 没有反应或报错
```

**解决：**
重新创建虚拟环境：
```bash
rm -rf rag_venv
python3 -m venv rag_venv
source rag_venv/bin/activate
pip install -r requirements.txt
```

### Q3: 依赖安装失败

**问题：**
```bash
pip install -r requirements.txt
# ModuleNotFoundError: No module named 'xxx'
```

**解决：**
确保虚拟环境已激活：
```bash
# 检查提示符，应该有 (rag_venv) 前缀
(rag_venv) lz@DESKTOP:~/my-rag-learning/my_rag$

# 如果没有，激活虚拟环境
source rag_venv/bin/activate

# 重新安装
pip install -r requirements.txt
```

### Q4: Docker 连接失败

**问题：**
```bash
docker ps
# Cannot connect to the Docker daemon
```

**解决：**
1. 确保 Docker Desktop 在 Windows 中已启动
2. 在 Docker Desktop 设置中启用 WSL 2 集成
3. 重启 WSL：
   ```bash
   # 在 Windows PowerShell 中
   wsl --shutdown
   # 重新打开 WSL
   ```

### Q5: 端口被占用

**问题：**
```bash
ERROR: for mysql-rag  Cannot start service mysql: 
Ports are not available: exposing port TCP 0.0.0.0:3306
```

**解决：**
检查端口占用：
```bash
# 在 WSL 中
sudo lsof -i :3306
sudo lsof -i :8000

# 或在 Windows PowerShell 中
netstat -ano | findstr "3306"
netstat -ano | findstr "8000"
```

## 🔧 开发技巧

### 1. 使用别名简化命令

在 `~/.bashrc` 中添加：
```bash
# RAG 项目别名
alias rag-cd='cd ~/my-rag-learning/my_rag'
alias rag-activate='source ~/my-rag-learning/my_rag/rag_venv/bin/activate'
alias rag-start='cd ~/my-rag-learning/my_rag && source rag_venv/bin/activate && python3 run.py'
alias rag-test='cd ~/my-rag-learning/my_rag && source rag_venv/bin/activate && python3 scripts/test_e2e.py'
```

然后：
```bash
source ~/.bashrc

# 使用别名
rag-cd        # 进入项目目录
rag-activate  # 激活虚拟环境
rag-start     # 启动服务
rag-test      # 运行测试
```

### 2. 使用 tmux 保持服务运行

```bash
# 安装 tmux
sudo apt install tmux

# 创建会话
tmux new -s rag

# 启动服务
cd ~/my-rag-learning/my_rag
source rag_venv/bin/activate
python3 run.py

# 分离会话（服务继续运行）
# 按 Ctrl+B，然后按 D

# 重新连接
tmux attach -t rag

# 关闭会话
tmux kill-session -t rag
```

### 3. 查看实时日志

```bash
# FastAPI 日志（如果使用 tmux）
tmux attach -t rag

# Docker 容器日志
docker logs -f mysql-rag
docker logs -f milvus-standalone
docker logs -f rag-redis
```

## 📊 性能监控

### 系统资源

```bash
# CPU 和内存使用
htop

# 磁盘使用
df -h

# Docker 资源使用
docker stats
```

### 服务状态

```bash
# 检查端口监听
sudo netstat -tlnp | grep -E '(3306|8000|9200|6379|19530)'

# 检查进程
ps aux | grep python3
ps aux | grep docker
```

## 🎯 最佳实践

1. **总是在虚拟环境中工作**
   ```bash
   source rag_venv/bin/activate
   ```

2. **使用 python3 而不是 python**
   ```bash
   python3 run.py  # ✅
   python run.py   # ❌
   ```

3. **定期更新依赖**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --upgrade
   ```

4. **使用脚本简化操作**
   ```bash
   bash setup_wsl.sh   # 初始化
   bash start_wsl.sh   # 启动
   ```

5. **保持 Docker 服务运行**
   - 确保 Docker Desktop 在 Windows 中启动
   - 启用 WSL 2 集成

## 📚 相关文档

- [README.md](README.md) - 项目总览
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - 部署指南
- [QUICKSTART.md](docs/QUICKSTART.md) - 快速开始

---

**祝你在 WSL 中使用愉快！** 🎉
