"""
应用配置模块
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "OpenSource Copilot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # API配置
    API_PREFIX: str = "/api"
    
    # CORS配置 - 生产环境需要添加实际域名
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://*.vercel.app",  # Vercel 预览部署
        "https://opensource-copilot.vercel.app",  # Vercel 生产
    ]
    
    # OpenAI配置 - 从环境变量读取
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "sk-MLw835bd40b8f415027d051be1c3eecc689453d3037j8sAO")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.gptsapi.net/v1")
    
    # GitHub配置
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    
    # OpenDigger配置
    OPENDIGGER_BASE_URL: str = "https://oss.x-lab.info/open_digger/github"
    
    # MaxKB配置
    MAXKB_BASE_URL: str = os.getenv("MAXKB_BASE_URL", "http://localhost:8080")
    MAXKB_API_KEY: str = os.getenv("MAXKB_API_KEY", "")
    
    # DataEase配置
    DATAEASE_BASE_URL: str = os.getenv("DATAEASE_BASE_URL", "http://localhost:8100")
    DATAEASE_API_KEY: str = os.getenv("DATAEASE_API_KEY", "")
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()

