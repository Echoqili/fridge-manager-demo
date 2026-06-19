"""营养分析接口测试。"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_nutrition_summary_empty(auth_client):
    """测试空库存时的营养摘要。"""
    resp = await auth_client.get("/api/v1/nutrition/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert data["total"] == 0
    # 所有分类计数应为 0
    for item in data["by_category"]:
        assert item["count"] == 0
    # 空库存应有多条建议
    assert len(data["advice"]) > 0


async def test_nutrition_summary_with_ingredients(auth_client):
    """测试有食材时的营养摘要。"""
    # 创建不同分类的食材
    await auth_client.post(
        "/api/v1/ingredients",
        json={"name": "西红柿", "category": "vegetable", "quantity": 3, "unit": "个"},
    )
    await auth_client.post(
        "/api/v1/ingredients",
        json={"name": "牛肉", "category": "meat", "quantity": 500, "unit": "克"},
    )
    await auth_client.post(
        "/api/v1/ingredients",
        json={"name": "牛奶", "category": "dairy", "quantity": 1, "unit": "瓶"},
    )

    resp = await auth_client.get("/api/v1/nutrition/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert data["total"] == 3

    # 验证分类统计
    category_map = {item["category"]: item["count"] for item in data["by_category"]}
    assert category_map["vegetable"] == 1
    assert category_map["meat"] == 1
    assert category_map["dairy"] == 1

    # 验证中文名标签存在
    labels = {item["category"]: item["label"] for item in data["by_category"]}
    assert labels["vegetable"] == "蔬菜"
    assert labels["meat"] == "肉类"
    assert labels["dairy"] == "蛋奶"


async def test_nutrition_summary_all_categories(auth_client):
    """测试覆盖所有 6 个分类的营养摘要。"""
    categories = [
        ("菠菜", "vegetable"),
        ("鸡肉", "meat"),
        ("鸡蛋", "dairy"),
        ("米饭", "staple"),
        ("苹果", "fruit"),
        ("盐", "other"),
    ]
    for name, cat in categories:
        await auth_client.post(
            "/api/v1/ingredients",
            json={"name": name, "category": cat, "quantity": 1, "unit": "个"},
        )

    resp = await auth_client.get("/api/v1/nutrition/summary")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 6

    # 所有分类都应有统计
    category_map = {item["category"]: item["count"] for item in data["by_category"]}
    for _, cat in categories:
        assert category_map[cat] == 1


async def test_nutrition_summary_advice_balanced(auth_client):
    """测试食材均衡时的建议。"""
    # 创建覆盖各分类的食材
    await auth_client.post(
        "/api/v1/ingredients",
        json={"name": "西兰花", "category": "vegetable", "quantity": 2, "unit": "个"},
    )
    await auth_client.post(
        "/api/v1/ingredients",
        json={"name": "猪肉", "category": "meat", "quantity": 1, "unit": "块"},
    )
    await auth_client.post(
        "/api/v1/ingredients",
        json={"name": "牛奶", "category": "dairy", "quantity": 1, "unit": "瓶"},
    )
    await auth_client.post(
        "/api/v1/ingredients",
        json={"name": "面条", "category": "staple", "quantity": 1, "unit": "包"},
    )
    await auth_client.post(
        "/api/v1/ingredients",
        json={"name": "香蕉", "category": "fruit", "quantity": 2, "unit": "根"},
    )

    resp = await auth_client.get("/api/v1/nutrition/summary")
    data = resp.json()["data"]
    # 均衡时应返回正面建议
    assert any("均衡" in a for a in data["advice"])


async def test_nutrition_requires_auth(async_client):
    """测试无认证访问营养接口被拒。"""
    resp = await async_client.get("/api/v1/nutrition/summary")
    assert resp.status_code == 401
