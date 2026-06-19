"""菜谱服务层：本地预设菜谱库 + AI 推荐。"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exceptions import NotFoundException
from models.ingredient import IngredientModel
from models.recipe import RecipeIngredientModel, RecipeModel
from schemas.recipe import RecipeIngredient, RecipeResponse, RecipeStep

logger = logging.getLogger(__name__)


# 本地预设菜谱库（至少 5 道菜）
LOCAL_RECIPES: list[dict[str, Any]] = [
    {
        "name": "西红柿炒蛋",
        "description": "家常经典菜，简单易做，酸甜可口。",
        "cook_time": 15,
        "calories": 220.0,
        "servings": 2,
        "ingredients": [
            {"ingredient_name": "西红柿", "amount": "2个", "is_required": True},
            {"ingredient_name": "鸡蛋", "amount": "3个", "is_required": True},
            {"ingredient_name": "盐", "amount": "适量", "is_required": False},
            {"ingredient_name": "糖", "amount": "少许", "is_required": False},
        ],
        "steps": [
            {"step": 1, "description": "西红柿洗净切块，鸡蛋打散加少许盐。"},
            {"step": 2, "description": "热锅冷油，倒入蛋液炒至凝固盛出。"},
            {"step": 3, "description": "锅中下西红柿翻炒出汁，加糖调味。"},
            {"step": 4, "description": "倒回鸡蛋翻炒均匀即可出锅。"},
        ],
    },
    {
        "name": "土豆炖牛肉",
        "description": "软烂入味的炖菜，营养丰富。",
        "cook_time": 60,
        "calories": 380.0,
        "servings": 3,
        "ingredients": [
            {"ingredient_name": "土豆", "amount": "2个", "is_required": True},
            {"ingredient_name": "牛肉", "amount": "300克", "is_required": True},
            {"ingredient_name": "胡萝卜", "amount": "1根", "is_required": False},
            {"ingredient_name": "酱油", "amount": "2勺", "is_required": False},
        ],
        "steps": [
            {"step": 1, "description": "牛肉切块焯水去血沫，土豆、胡萝卜切块。"},
            {"step": 2, "description": "锅中放油，下牛肉翻炒上色，加酱油。"},
            {"step": 3, "description": "加水没过牛肉，大火烧开转小火炖 40 分钟。"},
            {"step": 4, "description": "加入土豆、胡萝卜继续炖 15 分钟至软烂。"},
        ],
    },
    {
        "name": "蒜蓉西兰花",
        "description": "清淡健康，保留蔬菜营养。",
        "cook_time": 10,
        "calories": 120.0,
        "servings": 2,
        "ingredients": [
            {"ingredient_name": "西兰花", "amount": "1颗", "is_required": True},
            {"ingredient_name": "大蒜", "amount": "4瓣", "is_required": True},
            {"ingredient_name": "盐", "amount": "适量", "is_required": False},
        ],
        "steps": [
            {"step": 1, "description": "西兰花掰小朵洗净，大蒜切末。"},
            {"step": 2, "description": "沸水焯烫西兰花 1 分钟捞出。"},
            {"step": 3, "description": "热锅下蒜末爆香，倒入西兰花翻炒。"},
            {"step": 4, "description": "加盐调味，翻炒均匀出锅。"},
        ],
    },
    {
        "name": "胡萝卜炒肉",
        "description": "色泽诱人，荤素搭配。",
        "cook_time": 20,
        "calories": 260.0,
        "servings": 2,
        "ingredients": [
            {"ingredient_name": "胡萝卜", "amount": "2根", "is_required": True},
            {"ingredient_name": "猪肉", "amount": "150克", "is_required": True},
            {"ingredient_name": "生抽", "amount": "1勺", "is_required": False},
        ],
        "steps": [
            {"step": 1, "description": "胡萝卜切丝，猪肉切丝用生抽腌制。"},
            {"step": 2, "description": "热锅下肉丝滑炒至变色盛出。"},
            {"step": 3, "description": "下胡萝卜丝翻炒至软。"},
            {"step": 4, "description": "倒回肉丝，调味翻炒均匀。"},
        ],
    },
    {
        "name": "牛奶麦片",
        "description": "快手早餐，营养均衡。",
        "cook_time": 5,
        "calories": 280.0,
        "servings": 1,
        "ingredients": [
            {"ingredient_name": "牛奶", "amount": "250ml", "is_required": True},
            {"ingredient_name": "麦片", "amount": "50克", "is_required": True},
            {"ingredient_name": "蜂蜜", "amount": "适量", "is_required": False},
        ],
        "steps": [
            {"step": 1, "description": "牛奶倒入锅中加热至温热（不要煮沸）。"},
            {"step": 2, "description": "麦片放入碗中。"},
            {"step": 3, "description": "将热牛奶倒入麦片中，搅拌均匀。"},
            {"step": 4, "description": "根据口味加入蜂蜜即可。"},
        ],
    },
]


def _build_recipe_response(
    recipe_data: dict[str, Any],
    source: str = "local",
    user_ingredients: list[str] | None = None,
) -> RecipeResponse:
    """根据菜谱字典构造响应对象。"""
    ingredients = [RecipeIngredient(**item) for item in recipe_data.get("ingredients", [])]
    steps = [RecipeStep(**item) for item in recipe_data.get("steps", [])]

    match_count = None
    if user_ingredients is not None:
        user_set = {name.lower() for name in user_ingredients}
        match_count = sum(1 for ing in ingredients if ing.ingredient_name.lower() in user_set)

    return RecipeResponse(
        recipe_id=recipe_data.get("recipe_id", ""),
        name=recipe_data["name"],
        description=recipe_data.get("description"),
        cook_time=recipe_data.get("cook_time"),
        calories=recipe_data.get("calories"),
        servings=recipe_data.get("servings"),
        steps=steps,
        image_url=recipe_data.get("image_url"),
        source=source,  # type: ignore[arg-type]
        ingredients=ingredients,
        match_count=match_count,
        created_at=recipe_data.get("created_at"),
    )


def _match_score(recipe_data: dict[str, Any], user_ingredients: list[str]) -> int:
    """计算菜谱与用户食材的匹配数。"""
    user_set = {name.lower() for name in user_ingredients}
    score = 0
    for item in recipe_data.get("ingredients", []):
        if item["ingredient_name"].lower() in user_set:
            score += 1
    return score


def _build_recipe_prompt(user_ingredients: list[str], limit: int) -> str:
    """构造让 LLM 生成菜谱的提示词。"""
    ingredients_text = "、".join(user_ingredients) if user_ingredients else "（用户未指定食材，请推荐家常快手菜）"
    return (
        f"你是一位专业的家庭厨师和营养顾问。请根据以下食材推荐 {limit} 道适合的家常菜谱。\n\n"
        f"可用食材：{ingredients_text}\n\n"
        "要求：\n"
        "1. 优先使用用户已有的食材，可以使用少量常见调味料（盐、酱油、糖等）。\n"
        "2. 菜谱应简单易做，适合普通家庭厨房。\n"
        "3. 返回严格的 JSON 数组格式，不要任何 Markdown 标记或其他文字。\n\n"
        "每道菜谱必须包含以下字段：\n"
        "- name: 菜谱名称（字符串）\n"
        "- description: 简短描述（字符串）\n"
        "- cook_time: 烹饪时间，单位分钟（整数）\n"
        "- calories: 每份热量，单位 kcal（数字）\n"
        "- servings: 份数（整数）\n"
        "- ingredients: 所需食材数组，每个元素包含 ingredient_name（名称）、amount（用量字符串）、is_required（布尔值）\n"
        "- steps: 烹饪步骤数组，每个元素包含 step（步骤序号整数）、description（步骤描述字符串）\n\n"
        "请确保 JSON 格式正确，可以被 Python json.loads 直接解析。"
    )


def _clean_json_content(content: str) -> str:
    """清理 LLM 返回内容中的 Markdown 代码块标记。"""
    content = content.strip()
    if content.startswith("```"):
        # 去除第一行的 ```json 或 ```
        content = content.split("\n", 1)[1]
    if content.endswith("```"):
        content = content.rsplit("\n", 1)[0]
    return content.strip()


def _parse_ai_recipes(raw_content: str) -> list[dict[str, Any]] | None:
    """解析 LLM 返回的 JSON 菜谱数组。"""
    try:
        content = _clean_json_content(raw_content)
        data = json.loads(content)
        if not isinstance(data, list):
            logger.warning("LLM 返回的菜谱不是数组格式")
            return None
        valid_recipes = []
        for item in data:
            if not isinstance(item, dict):
                continue
            # 规范化字段
            recipe = {
                "name": item.get("name", "AI 推荐菜谱"),
                "description": item.get("description", ""),
                "cook_time": int(item.get("cook_time", 15)),
                "calories": float(item.get("calories", 0)),
                "servings": int(item.get("servings", 2)),
                "ingredients": item.get("ingredients", []),
                "steps": item.get("steps", []),
                "recipe_id": "",
            }
            # 确保 ingredients 字段格式正确
            normalized_ingredients = []
            for ing in recipe["ingredients"]:
                if isinstance(ing, dict):
                    normalized_ingredients.append(
                        {
                            "ingredient_name": ing.get("ingredient_name", ing.get("name", "食材")),
                            "amount": str(ing.get("amount", "适量")),
                            "is_required": bool(ing.get("is_required", True)),
                        }
                    )
            recipe["ingredients"] = normalized_ingredients

            # 确保 steps 字段格式正确
            normalized_steps = []
            for step in recipe["steps"]:
                if isinstance(step, dict):
                    normalized_steps.append(
                        {
                            "step": int(step.get("step", len(normalized_steps) + 1)),
                            "description": str(step.get("description", step.get("desc", ""))),
                        }
                    )
            recipe["steps"] = normalized_steps

            valid_recipes.append(recipe)
        return valid_recipes
    except json.JSONDecodeError as exc:
        logger.warning("LLM 返回内容 JSON 解析失败: %s", exc)
        return None
    except Exception as exc:  # noqa: BLE001
        logger.warning("解析 LLM 菜谱失败: %s", exc)
        return None


async def _generate_recipes_with_openai(user_ingredients: list[str], limit: int) -> list[dict[str, Any]] | None:
    """使用 OpenAI GPT 生成菜谱。"""
    if not settings.OPENAI_API_KEY:
        return None
    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的家庭厨师，擅长根据现有食材设计简单可口的家常菜谱。"},
                {"role": "user", "content": _build_recipe_prompt(user_ingredients, limit)},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        content = response.choices[0].message.content or ""
        recipes = _parse_ai_recipes(content)
        if recipes:
            logger.info("OpenAI 成功生成 %d 道菜谱", len(recipes))
        return recipes
    except Exception as exc:  # noqa: BLE001
        logger.warning("OpenAI 菜谱生成失败，将降级到本地库: %s", exc)
        return None


def _deduplicate_recipes(
    ai_recipes: list[RecipeResponse],
    local_recipes: list[RecipeResponse],
    user_ingredients: list[str],
    limit: int,
) -> list[RecipeResponse]:
    """合并 AI 菜谱和本地菜谱，按匹配数排序并去重。"""
    seen_names = set()
    combined: list[RecipeResponse] = []

    # AI 菜谱优先
    for recipe in ai_recipes:
        name_lower = recipe.name.lower()
        if name_lower not in seen_names:
            combined.append(recipe)
            seen_names.add(name_lower)

    # 补充本地菜谱
    for recipe in local_recipes:
        name_lower = recipe.name.lower()
        if name_lower not in seen_names:
            combined.append(recipe)
            seen_names.add(name_lower)

    # 按匹配数降序排序；匹配数相同时，AI 生成的菜谱优先
    combined.sort(
        key=lambda r: (r.match_count or 0, r.source == "ai"),
        reverse=True,
    )
    return combined[:limit]


async def _save_ai_recipes_to_db(
    db: AsyncSession,
    user_id: str,
    ai_recipes: list[dict[str, Any]],
) -> list[RecipeModel]:
    """将 AI 生成的菜谱持久化到数据库，并返回保存后的 ORM 对象。"""
    saved: list[RecipeModel] = []
    for recipe_data in ai_recipes:
        recipe = RecipeModel(
            user_id=user_id,
            name=recipe_data["name"],
            description=recipe_data.get("description"),
            cook_time=recipe_data.get("cook_time"),
            calories=recipe_data.get("calories"),
            servings=recipe_data.get("servings"),
            steps=recipe_data.get("steps", []) or [],
            source="ai",
        )
        for ing in recipe_data.get("ingredients", []):
            recipe.ingredients.append(
                RecipeIngredientModel(
                    ingredient_name=ing["ingredient_name"],
                    amount=ing.get("amount"),
                    is_required=ing.get("is_required", True),
                )
            )
        db.add(recipe)
        saved.append(recipe)
    await db.commit()
    for recipe in saved:
        await db.refresh(recipe)
    logger.info("持久化 %d 道 AI 菜谱到数据库", len(saved))
    return saved


def _recipe_model_to_response(
    recipe: RecipeModel,
    user_ingredients: list[str],
) -> RecipeResponse:
    """将 RecipeModel ORM 对象转换为 RecipeResponse。"""
    ingredients = [
        RecipeIngredient(
            ingredient_name=ing.ingredient_name,
            amount=ing.amount,
            is_required=ing.is_required,
        )
        for ing in (recipe.ingredients or [])
    ]
    steps = [RecipeStep(**step) for step in (recipe.steps or [])]

    user_set = {name.lower() for name in user_ingredients}
    match_count = sum(1 for ing in ingredients if ing.ingredient_name.lower() in user_set)

    return RecipeResponse(
        recipe_id=recipe.recipe_id,
        name=recipe.name,
        description=recipe.description,
        cook_time=recipe.cook_time,
        calories=recipe.calories,
        servings=recipe.servings,
        steps=steps,
        image_url=recipe.image_url,
        source=recipe.source,  # type: ignore[arg-type]
        ingredients=ingredients,
        match_count=match_count,
        created_at=recipe.created_at,
    )


async def recommend_recipes(
    db: AsyncSession,
    user_id: str,
    user_ingredients: list[str] | None = None,
    limit: int = 5,
) -> list[RecipeResponse]:
    """基于现有食材推荐菜谱。

    优先调用 AI 生成个性化菜谱；AI 不可用时，降级到本地预设菜谱库。
    """
    # 若未指定食材，则从数据库读取用户库存
    if user_ingredients is None:
        result = await db.execute(select(IngredientModel).where(IngredientModel.user_id == user_id))
        user_ingredients = [ing.name for ing in result.scalars().all()]

    # 本地菜谱匹配排序
    scored = [(recipe, _match_score(recipe, user_ingredients)) for recipe in LOCAL_RECIPES]
    scored.sort(key=lambda x: x[1], reverse=True)
    local_responses = [
        _build_recipe_response(recipe_data, source="local", user_ingredients=user_ingredients)
        for recipe_data, _ in scored
    ]

    # AI 生成菜谱并持久化到数据库
    ai_recipes: list[RecipeResponse] = []
    generated = await _generate_recipes_with_openai(user_ingredients, limit)
    if generated:
        saved_models = await _save_ai_recipes_to_db(db, user_id, generated)
        ai_recipes = [_recipe_model_to_response(model, user_ingredients=user_ingredients) for model in saved_models]
        logger.info("AI 菜谱推荐返回 %d 道菜谱", len(ai_recipes))
    else:
        logger.info("AI 菜谱生成不可用，使用本地菜谱库")

    # 合并 AI 和本地菜谱，按匹配数排序
    return _deduplicate_recipes(ai_recipes, local_responses, user_ingredients, limit)


async def get_recipe_by_id(db: AsyncSession, recipe_id: str) -> RecipeResponse:
    """根据 ID 获取菜谱详情。

    本地预设菜谱使用固定 recipe_id（基于索引），数据库菜谱从表中查询。
    """
    # 先尝试本地预设菜谱（recipe_id 形如 local-0、local-1）
    if recipe_id.startswith("local-"):
        try:
            idx = int(recipe_id.split("-", 1)[1])
            if 0 <= idx < len(LOCAL_RECIPES):
                recipe_data = dict(LOCAL_RECIPES[idx])
                recipe_data["recipe_id"] = recipe_id
                return _build_recipe_response(recipe_data, source="local")
        except (ValueError, IndexError):
            pass
        raise NotFoundException(message="菜谱不存在")

    # 数据库查询（支持 AI 生成菜谱持久化后的详情查询）
    result = await db.execute(select(RecipeModel).where(RecipeModel.recipe_id == recipe_id))
    recipe = result.scalar_one_or_none()
    if recipe is None:
        raise NotFoundException(message="菜谱不存在")

    return _recipe_model_to_response(recipe, user_ingredients=[])


def get_local_recipe_index(recipe_name: str) -> int | None:
    """根据菜名获取本地菜谱索引，便于生成稳定的 recipe_id。"""
    for idx, recipe in enumerate(LOCAL_RECIPES):
        if recipe["name"] == recipe_name:
            return idx
    return None
