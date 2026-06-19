"""食材 CRUD 测试。"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

pytestmark = pytest.mark.asyncio


async def test_create_ingredient(auth_client):
    """测试创建食材。"""
    payload = {
        "name": "黄瓜",
        "category": "vegetable",
        "quantity": 2.0,
        "unit": "根",
        "storage_location": "fridge",
        "expiry_date": str(date.today() + timedelta(days=5)),
    }
    resp = await auth_client.post("/api/v1/ingredients", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["name"] == "黄瓜"
    assert body["data"]["category"] == "vegetable"
    assert body["data"]["quantity"] == 2.0


async def test_list_ingredients(auth_client):
    """测试获取食材列表。"""
    # 先创建两条
    await auth_client.post(
        "/api/v1/ingredients",
        json={"name": "西红柿", "category": "vegetable", "quantity": 3, "unit": "个"},
    )
    await auth_client.post(
        "/api/v1/ingredients",
        json={"name": "牛奶", "category": "dairy", "quantity": 1, "unit": "瓶"},
    )
    resp = await auth_client.get("/api/v1/ingredients")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["total"] >= 2


async def test_list_ingredients_by_category(auth_client):
    """测试按分类过滤食材。"""
    await auth_client.post(
        "/api/v1/ingredients",
        json={"name": "菠菜", "category": "vegetable", "quantity": 1, "unit": "把"},
    )
    await auth_client.post(
        "/api/v1/ingredients",
        json={"name": "牛肉", "category": "meat", "quantity": 500, "unit": "克"},
    )
    resp = await auth_client.get("/api/v1/ingredients?category=meat")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert all(item["category"] == "meat" for item in body["data"]["items"])


async def test_update_ingredient(auth_client):
    """测试更新食材。"""
    create_resp = await auth_client.post(
        "/api/v1/ingredients",
        json={"name": "土豆", "category": "vegetable", "quantity": 1, "unit": "个"},
    )
    ingredient_id = create_resp.json()["data"]["ingredient_id"]
    resp = await auth_client.put(
        f"/api/v1/ingredients/{ingredient_id}",
        json={"quantity": 5.0, "unit": "个"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["quantity"] == 5.0


async def test_delete_ingredient(auth_client):
    """测试删除食材。"""
    create_resp = await auth_client.post(
        "/api/v1/ingredients",
        json={"name": "洋葱", "category": "vegetable", "quantity": 1, "unit": "个"},
    )
    ingredient_id = create_resp.json()["data"]["ingredient_id"]
    resp = await auth_client.delete(f"/api/v1/ingredients/{ingredient_id}")
    assert resp.status_code == 200
    # 再次获取列表应不包含已删除项
    list_resp = await auth_client.get("/api/v1/ingredients")
    ids = [item["ingredient_id"] for item in list_resp.json()["data"]["items"]]
    assert ingredient_id not in ids


async def test_get_expiring_ingredients(auth_client):
    """测试获取临期食材。"""
    # 创建一个即将过期的食材
    await auth_client.post(
        "/api/v1/ingredients",
        json={
            "name": "酸奶",
            "category": "dairy",
            "quantity": 1,
            "unit": "瓶",
            "expiry_date": str(date.today() + timedelta(days=1)),
        },
    )
    # 创建一个未过期的食材
    await auth_client.post(
        "/api/v1/ingredients",
        json={
            "name": "苹果",
            "category": "fruit",
            "quantity": 3,
            "unit": "个",
            "expiry_date": str(date.today() + timedelta(days=30)),
        },
    )
    resp = await auth_client.get("/api/v1/ingredients/expiring?days=3")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    names = [item["name"] for item in body["data"]["items"]]
    assert "酸奶" in names
    assert "苹果" not in names


async def test_ingredient_requires_auth(async_client):
    """测试无认证访问食材接口被拒。"""
    resp = await async_client.get("/api/v1/ingredients")
    assert resp.status_code == 401
