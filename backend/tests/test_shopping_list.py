"""购物清单接口测试。"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_get_empty_shopping_list(auth_client):
    """测试获取空购物清单。"""
    resp = await auth_client.get("/api/v1/shopping-list")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"] == []


async def test_add_shopping_item(auth_client):
    """测试添加购物清单条目。"""
    resp = await auth_client.post(
        "/api/v1/shopping-list",
        json={"name": "西红柿", "quantity": "2个", "checked": False},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["name"] == "西红柿"
    assert body["data"]["quantity"] == "2个"
    assert body["data"]["checked"] is False
    assert "item_id" in body["data"]


async def test_batch_add_items(auth_client):
    """测试批量添加购物清单条目。"""
    resp = await auth_client.post(
        "/api/v1/shopping-list/batch",
        json={
            "items": [
                {"name": "鸡蛋", "quantity": "1盒"},
                {"name": "牛奶", "quantity": "2瓶"},
            ]
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert len(body["data"]) == 2


async def test_update_shopping_item(auth_client):
    """测试更新购物清单条目（勾选）。"""
    # 先添加
    resp = await auth_client.post(
        "/api/v1/shopping-list",
        json={"name": "土豆", "quantity": "3个"},
    )
    item_id = resp.json()["data"]["item_id"]

    # 勾选
    resp = await auth_client.put(
        f"/api/v1/shopping-list/{item_id}",
        json={"checked": True},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["checked"] is True


async def test_delete_shopping_item(auth_client):
    """测试删除购物清单条目。"""
    resp = await auth_client.post(
        "/api/v1/shopping-list",
        json={"name": "洋葱", "quantity": "1个"},
    )
    item_id = resp.json()["data"]["item_id"]

    resp = await auth_client.delete(f"/api/v1/shopping-list/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["code"] == 0

    # 确认已删除
    resp = await auth_client.get("/api/v1/shopping-list")
    items = resp.json()["data"]
    assert all(i["item_id"] != item_id for i in items)


async def test_clear_shopping_list(auth_client):
    """测试清空购物清单。"""
    await auth_client.post(
        "/api/v1/shopping-list/batch",
        json={"items": [{"name": "盐"}, {"name": "酱油"}]},
    )
    resp = await auth_client.delete("/api/v1/shopping-list")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["deleted"] == 2

    # 确认已清空
    resp = await auth_client.get("/api/v1/shopping-list")
    assert resp.json()["data"] == []


async def test_shopping_list_requires_auth(async_client):
    """测试无认证访问购物清单被拒。"""
    resp = await async_client.get("/api/v1/shopping-list")
    assert resp.status_code == 401
