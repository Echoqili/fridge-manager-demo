"""认证相关测试。"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_register_success(async_client):
    """测试注册成功。"""
    payload = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "newpass123",
    }
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["username"] == "newuser"
    assert body["data"]["email"] == "new@example.com"


async def test_register_duplicate(async_client, registered_user):
    """测试重复注册失败。"""
    payload = {
        "username": registered_user["username"],
        "email": "another@example.com",
        "password": "anotherpass123",
    }
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400
    body = resp.json()
    assert body["code"] == 40001


async def test_login_success(async_client, registered_user):
    """测试登录成功。"""
    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"username": registered_user["username"], "password": registered_user["password"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]
    assert body["data"]["token_type"] == "bearer"


async def test_login_wrong_password(async_client, registered_user):
    """测试密码错误登录失败。"""
    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"username": registered_user["username"], "password": "wrongpass"},
    )
    assert resp.status_code == 401
    body = resp.json()
    assert body["code"] == 40101


async def test_me_with_token(auth_client):
    """测试带 Token 获取当前用户。"""
    resp = await auth_client.get("/api/v1/auth/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["username"] == "testuser"


async def test_me_without_token(async_client):
    """测试无 Token 访问被拒。"""
    resp = await async_client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_refresh_token(async_client, registered_user):
    """测试刷新令牌。"""
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"username": registered_user["username"], "password": registered_user["password"]},
    )
    refresh_token = login_resp.json()["data"]["refresh_token"]
    resp = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert "access_token" in body["data"]
