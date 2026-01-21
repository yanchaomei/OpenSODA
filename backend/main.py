"""
OpenSource Copilot - 开源社区智能运营 Agent
主入口文件
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import router as api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    print("🚀 OpenSource Copilot is starting...")
    print(f"📍 Environment: {'production' if not settings.DEBUG else 'development'}")
    yield
    # Shutdown
    print("👋 OpenSource Copilot is shutting down...")


app = FastAPI(
    title="OpenSource Copilot",
    description="开源社区智能运营 Agent - 基于多Agent架构的开源社区运营助手",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS配置 - 生产环境允许所有来源（Railway health check 需要）
cors_origins = settings.CORS_ORIGINS if settings.DEBUG else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """根路径 - 返回应用信息"""
    return {
        "name": "OpenSource Copilot",
        "version": "1.0.0",
        "status": "running",
        "description": "开源社区智能运营 Agent"
    }


@app.get("/health")
async def health_check():
    """
    健康检查端点 - Railway/K8s 使用
    返回简单状态，确保快速响应
    """
    return {"status": "healthy", "service": "opensource-copilot"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

