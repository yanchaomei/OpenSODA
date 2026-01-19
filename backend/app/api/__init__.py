"""
API路由模块
"""
from fastapi import APIRouter

from .chat import router as chat_router
from .analysis import router as analysis_router
from .health import router as health_router
from .dashboard import router as dashboard_router

router = APIRouter()

# 注册子路由
router.include_router(chat_router, prefix="/chat", tags=["Chat"])
router.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
router.include_router(health_router, prefix="/health", tags=["Health"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])

