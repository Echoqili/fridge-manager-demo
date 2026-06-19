"""数据库连接与会话管理。"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from core.config import settings

# 测试环境使用内存数据库
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")


def _get_database_url() -> str:
    """获取当前使用的数据库 URL，测试环境优先使用内存库。"""
    if os.getenv("TESTING") == "1":
        return TEST_DATABASE_URL
    return settings.DATABASE_URL


# 异步引擎
engine = create_async_engine(
    _get_database_url(),
    echo=settings.is_development,
    future=True,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# ORM 基类
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话依赖。"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """初始化数据库：创建所有表。"""
    # 确保所有模型被导入，以便 Base.metadata 包含全部表
    from models import ingredient, recipe, shopping_list, user  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_db() -> None:
    """关闭数据库连接池。"""
    await engine.dispose()
