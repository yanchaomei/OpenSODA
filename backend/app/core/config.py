"""
应用配置模块
"""
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "OpenSource Copilot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API配置
    API_PREFIX: str = "/api"
    
    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # OpenAI配置
    OPENAI_API_KEY: str = "sk-MLw835bd40b8f415027d051be1c3eecc689453d3037j8sAO"
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_BASE_URL: str = "https://api.gptsapi.net/v1"
    
    # GitHub配置
    GITHUB_TOKEN: str = ""
    
    # OpenDigger配置
    OPENDIGGER_BASE_URL: str = "https://oss.x-lab.info/open_digger/github"
    
    # MaxKB配置
    MAXKB_BASE_URL: str = "http://localhost:8080"
    MAXKB_API_KEY: str = ""
    
    # DataEase配置
    DATAEASE_BASE_URL: str = "http://localhost:8100"
    DATAEASE_API_KEY: str = ""
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/opensource_copilot"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()

