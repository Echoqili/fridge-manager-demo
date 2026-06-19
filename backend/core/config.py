"""应用配置模块。

使用 pydantic-settings 与 os.getenv 读取环境变量，集中管理所有配置项。
"""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


def _parse_origins(raw: str) -> list[str]:
    """解析 CORS 来源字符串，支持逗号分隔。"""
    if not raw:
        return ["http://localhost:3000"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


class Settings:
    """全局配置类，从环境变量读取。"""

    # 数据库配置
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "sqlite")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/fridge.db")

    # JWT 配置
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "fridge-manager-dev-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "15"))
    JWT_REFRESH_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))

    # OpenAI 配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # 智谱 AI 配置
    ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "")
    ZHIPU_MODEL: str = os.getenv("ZHIPU_MODEL", "glm-4v")

    # 应用配置
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CORS_ORIGINS: list[str] = _parse_origins(os.getenv("CORS_ORIGINS", "http://localhost:3000"))

    # 错误码
    CODE_SUCCESS: int = 0
    CODE_PARAM_ERROR: int = 40001
    CODE_AUTH_ERROR: int = 40101
    CODE_NOT_FOUND: int = 40401
    CODE_SERVER_ERROR: int = 50001

    @property
    def is_development(self) -> bool:
        """是否为开发环境。"""
        return self.ENVIRONMENT == "development"


@lru_cache
def get_settings() -> Settings:
    """获取配置单例。"""
    return Settings()


settings = get_settings()
