"""
快速启动脚本
"""
import uvicorn

if __name__ == "__main__":
    # 关闭 reload 避免监控 volumes 目录权限问题
    # 如需热重载，请手动重启服务
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )

