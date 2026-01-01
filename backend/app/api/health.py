"""
Health API - 系统健康检查
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
import asyncio

router = APIRouter()


class ServiceStatus(BaseModel):
    """服务状态"""
    name: str
    status: str  # healthy, unhealthy, unknown
    latency_ms: float = 0


class HealthStatus(BaseModel):
    """系统健康状态"""
    status: str
    services: Dict[str, ServiceStatus]


@router.get("/", response_model=HealthStatus)
async def check_health():
    """
    检查系统健康状态
    """
    services = {}
    
    # 检查各服务状态
    checks = await asyncio.gather(
        check_opendigger(),
        check_openai(),
        check_database(),
        return_exceptions=True
    )
    
    service_names = ["opendigger", "openai", "database"]
    for name, result in zip(service_names, checks):
        if isinstance(result, Exception):
            services[name] = ServiceStatus(
                name=name,
                status="unhealthy",
                latency_ms=0
            )
        else:
            services[name] = result
    
    # 判断总体状态
    all_healthy = all(s.status == "healthy" for s in services.values())
    overall_status = "healthy" if all_healthy else "degraded"
    
    return HealthStatus(
        status=overall_status,
        services=services
    )


async def check_opendigger() -> ServiceStatus:
    """检查 OpenDigger API 状态"""
    import httpx
    import time
    
    try:
        start = time.time()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://oss.x-lab.info/open_digger/github/X-lab2017/open-digger/openrank.json",
                timeout=5.0
            )
            latency = (time.time() - start) * 1000
            
            if response.status_code == 200:
                return ServiceStatus(
                    name="opendigger",
                    status="healthy",
                    latency_ms=round(latency, 2)
                )
    except Exception:
        pass
    
    return ServiceStatus(
        name="opendigger",
        status="unhealthy",
        latency_ms=0
    )


async def check_openai() -> ServiceStatus:
    """检查 OpenAI API 状态"""
    from app.core.config import settings
    import httpx
    import time
    
    if not settings.OPENAI_API_KEY:
        return ServiceStatus(
            name="openai",
            status="unknown",
            latency_ms=0
        )
    
    try:
        start = time.time()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.OPENAI_BASE_URL}/models",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                timeout=5.0
            )
            latency = (time.time() - start) * 1000
            
            if response.status_code == 200:
                return ServiceStatus(
                    name="openai",
                    status="healthy",
                    latency_ms=round(latency, 2)
                )
    except Exception:
        pass
    
    return ServiceStatus(
        name="openai",
        status="unhealthy",
        latency_ms=0
    )


async def check_database() -> ServiceStatus:
    """检查数据库状态"""
    # TODO: 实现数据库健康检查
    return ServiceStatus(
        name="database",
        status="unknown",
        latency_ms=0
    )

