"""pytest 测试夹具。"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

# 设置测试环境变量（必须在导入应用之前）
os.environ["TESTING"] = "1"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-pytest-only"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.security import hash_password

# 在导入 main 之前导入所有模型，确保 metadata 完整
from models import ingredient, recipe, shopping_list, user  # noqa: F401
from models.database import Base, get_db
from models.user import UserModel
from schemas.ingredient import IngredientCreate


@pytest_asyncio.fixture
async def db_engine():
    """创建内存数据库引擎。"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """数据库会话夹具。"""
    session_factory = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP 测试客户端，使用测试数据库会话覆盖依赖。"""
    from main import app

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def registered_user(async_client: AsyncClient) -> dict:
    """注册一个测试用户并返回登录信息。"""
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
    }
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 200, resp.text
    return payload


@pytest_asyncio.fixture
async def auth_token(async_client: AsyncClient, registered_user: dict) -> str:
    """登录并返回 access_token。"""
    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"username": registered_user["username"], "password": registered_user["password"]},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    return data["access_token"]


@pytest_asyncio.fixture
async def auth_client(async_client: AsyncClient, auth_token: str) -> AsyncClient:
    """带 JWT 的 HTTP 客户端。"""
    async_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return async_client


@pytest_asyncio.fixture
async def sample_user(db_session: AsyncSession) -> UserModel:
    """直接在数据库创建一个测试用户。"""
    new_user = UserModel(
        username="sampleuser",
        email="sample@example.com",
        hashed_password=hash_password("samplepass123"),
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)
    return new_user


@pytest_asyncio.fixture
async def sample_ingredient(db_session: AsyncSession, sample_user: UserModel):
    """创建一个示例食材。"""
    from services import ingredient_service

    data = IngredientCreate(
        name="西红柿",
        category="vegetable",
        quantity=3.0,
        unit="个",
        storage_location="fridge",
    )
    return await ingredient_service.create_ingredient(db_session, sample_user.user_id, data)
