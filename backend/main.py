"""
OpenSource Copilot - 开源社区智能运营 Agent
主入口文件
"""
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
    yield
    # Shutdown
    print("👋 OpenSource Copilot is shutting down...")


app = FastAPI(
    title="OpenSource Copilot",
    description="开源社区智能运营 Agent - 基于多Agent架构的开源社区运营助手",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """健康检查"""
    return {
        "name": "OpenSource Copilot",
        "version": "1.0.0",
        "status": "running",
        "description": "开源社区智能运营 Agent"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

