"""菜谱推荐测试。"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

pytestmark = pytest.mark.asyncio


async def test_recommend_recipes_default(auth_client):
    """测试默认菜谱推荐（无指定食材，使用库存）。"""
    resp = await auth_client.get("/api/v1/recipes/recommend")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    recipes = body["data"]
    assert isinstance(recipes, list)
    assert len(recipes) > 0
    # 应返回本地预设菜谱
    names = [r["name"] for r in recipes]
    assert "西红柿炒蛋" in names


async def test_recommend_recipes_with_ingredients(auth_client):
    """测试指定食材推荐菜谱。"""
    resp = await auth_client.get("/api/v1/recipes/recommend?ingredients=西红柿,鸡蛋,土豆,牛肉")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    recipes = body["data"]
    # 西红柿炒蛋应排在前面（匹配数高）
    assert recipes[0]["name"] == "西红柿炒蛋"
    assert recipes[0]["match_count"] == 2


async def test_recommend_recipes_limit(auth_client):
    """测试推荐数量限制。"""
    resp = await auth_client.get("/api/v1/recipes/recommend?limit=2")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) <= 2


async def test_get_local_recipe_by_id(auth_client):
    """测试获取本地菜谱详情。"""
    resp = await auth_client.get("/api/v1/recipes/local-0")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["name"] == "西红柿炒蛋"
    assert body["data"]["source"] == "local"
    assert len(body["data"]["steps"]) > 0
    assert len(body["data"]["ingredients"]) > 0


async def test_get_recipe_not_found(auth_client):
    """测试获取不存在的菜谱。"""
    resp = await auth_client.get("/api/v1/recipes/local-999")
    assert resp.status_code == 404
    body = resp.json()
    assert body["code"] == 40401


async def test_recipe_contains_required_fields(auth_client):
    """测试菜谱响应包含必需字段。"""
    resp = await auth_client.get("/api/v1/recipes/recommend?limit=1")
    body = resp.json()
    recipe = body["data"][0]
    assert "recipe_id" in recipe
    assert "name" in recipe
    assert "description" in recipe
    assert "cook_time" in recipe
    assert "calories" in recipe
    assert "servings" in recipe
    assert "steps" in recipe
    assert "ingredients" in recipe
    assert "source" in recipe


async def test_recommend_recipes_with_ai(auth_client):
    """测试 AI 生成菜谱时优先返回 AI 推荐并持久化到数据库。"""
    ai_response = {
        "choices": [
            {
                "message": {
                    "content": '[{"name": "番茄鸡蛋汤", "description": "清淡开胃汤品", "cook_time": 10, "calories": 120, "servings": 2, "ingredients": [{"ingredient_name": "西红柿", "amount": "2个", "is_required": true}, {"ingredient_name": "鸡蛋", "amount": "2个", "is_required": true}], "steps": [{"step": 1, "description": "西红柿切块，鸡蛋打散"}, {"step": 2, "description": "水烧开加西红柿煮3分钟"}, {"step": 3, "description": "淋入蛋液，加盐调味"}]}]'
                }
            }
        ]
    }

    with (
        patch("services.recipe_service.AsyncOpenAI") as mock_client_class,
        patch("services.recipe_service.settings.OPENAI_API_KEY", "test-key"),
    ):
        mock_client = mock_client_class.return_value
        # 正确 mock choices 链式调用
        mock_choice = AsyncMock()
        mock_choice.message.content = ai_response["choices"][0]["message"]["content"]
        mock_completion = AsyncMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

        resp = await auth_client.get("/api/v1/recipes/recommend?ingredients=西红柿,鸡蛋&limit=3")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        recipes = body["data"]
        assert len(recipes) > 0
        # AI 生成菜谱应排在前面
        assert recipes[0]["name"] == "番茄鸡蛋汤"
        assert recipes[0]["source"] == "ai"
        assert recipes[0]["match_count"] == 2
        assert len(recipes[0]["steps"]) == 3
        assert len(recipes[0]["ingredients"]) == 2
        # AI 菜谱已持久化，recipe_id 应为数据库 UUID（不再是 ai-0）
        assert not recipes[0]["recipe_id"].startswith("ai-")

        # 保存 recipe_id 供下一个测试验证详情查询
        return recipes[0]["recipe_id"]


async def test_get_ai_recipe_detail(auth_client):
    """测试 AI 生成菜谱持久化后可通过 recipe_id 查询详情。"""
    ai_response = {
        "choices": [
            {
                "message": {
                    "content": '[{"name": "青椒肉丝", "description": "下饭快手菜", "cook_time": 20, "calories": 250, "servings": 2, "ingredients": [{"ingredient_name": "青椒", "amount": "3个", "is_required": true}, {"ingredient_name": "猪肉", "amount": "200克", "is_required": true}], "steps": [{"step": 1, "description": "青椒切丝，猪肉切丝"}, {"step": 2, "description": "热锅炒熟肉丝"}, {"step": 3, "description": "加入青椒翻炒调味"}]}]'
                }
            }
        ]
    }

    with (
        patch("services.recipe_service.AsyncOpenAI") as mock_client_class,
        patch("services.recipe_service.settings.OPENAI_API_KEY", "test-key"),
    ):
        mock_client = mock_client_class.return_value
        mock_choice = AsyncMock()
        mock_choice.message.content = ai_response["choices"][0]["message"]["content"]
        mock_completion = AsyncMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

        resp = await auth_client.get("/api/v1/recipes/recommend?ingredients=青椒,猪肉")
        recipe_id = resp.json()["data"][0]["recipe_id"]

    # 查询详情
    resp = await auth_client.get(f"/api/v1/recipes/{recipe_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    detail = body["data"]
    assert detail["name"] == "青椒肉丝"
    assert detail["source"] == "ai"
    assert len(detail["ingredients"]) == 2
    assert len(detail["steps"]) == 3


async def test_recommend_recipes_ai_fallback(auth_client):
    """测试 AI 生成失败时降级到本地菜谱库。"""
    with (
        patch("services.recipe_service.AsyncOpenAI") as mock_client_class,
        patch("services.recipe_service.settings.OPENAI_API_KEY", "test-key"),
    ):
        mock_client = mock_client_class.return_value
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API 错误"))

        resp = await auth_client.get("/api/v1/recipes/recommend?ingredients=西红柿,鸡蛋&limit=3")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        recipes = body["data"]
        assert len(recipes) > 0
        # 应回退到本地菜谱
        names = [r["name"] for r in recipes]
        assert "西红柿炒蛋" in names


async def test_recommend_recipes_ai_duplicate_handling(auth_client):
    """测试 AI 生成菜谱与本地重复时去重。"""
    ai_response_content = (
        '[{"name": "西红柿炒蛋", "description": "家常经典", "cook_time": 15, "calories": 220, "servings": 2, '
        '"ingredients": [{"ingredient_name": "西红柿", "amount": "2个", "is_required": true}, '
        '{"ingredient_name": "鸡蛋", "amount": "3个", "is_required": true}], '
        '"steps": [{"step": 1, "description": "切块打散"}, {"step": 2, "description": "炒熟出锅"}]}]'
    )

    with (
        patch("services.recipe_service.AsyncOpenAI") as mock_client_class,
        patch("services.recipe_service.settings.OPENAI_API_KEY", "test-key"),
    ):
        mock_client = mock_client_class.return_value
        mock_choice = AsyncMock()
        mock_choice.message.content = ai_response_content
        mock_completion = AsyncMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

        resp = await auth_client.get("/api/v1/recipes/recommend?ingredients=西红柿,鸡蛋&limit=5")
        body = resp.json()
        recipes = body["data"]
        # 西红柿炒蛋只应出现一次（AI 优先）
        names = [r["name"] for r in recipes]
        assert names.count("西红柿炒蛋") == 1
