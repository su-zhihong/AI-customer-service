"""
文件路径: backend/app/config.py
配置模块：从 .env 文件读取所有配置项，使用 Pydantic Settings 进行校验。
"""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()


class Settings(BaseSettings):
    """应用配置类，所有配置项集中管理"""

    # OpenAI 配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Redis 配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    # JWT 配置
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "default-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./seckill.db")

    # 服务配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局单例配置对象
settings = Settings()
