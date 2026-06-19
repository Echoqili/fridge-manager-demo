"""菜谱路由：推荐与详情。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from models.database import get_db
from models.user import UserModel
from schemas.common import ApiResponse
from schemas.recipe import RecipeResponse
from services import recipe_service

router = APIRouter(prefix="/recipes", tags=["菜谱推荐"])


@router.get("/recommend", response_model=ApiResponse[list[RecipeResponse]])
async def recommend_recipes(
    limit: int = Query(default=5, ge=1, le=20, description="推荐数量"),
    ingredients: str | None = Query(default=None, description="指定食材列表，逗号分隔"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> ApiResponse[list[RecipeResponse]]:
    """基于现有食材推荐菜谱。"""
    user_ingredients = None
    if ingredients:
        user_ingredients = [i.strip() for i in ingredients.split(",") if i.strip()]
    recipes = await recipe_service.recommend_recipes(
        db, current_user.user_id, user_ingredients=user_ingredients, limit=limit
    )
    return ApiResponse.success(data=recipes)


@router.get("/{recipe_id}", response_model=ApiResponse[RecipeResponse])
async def get_recipe(
    recipe_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),  # noqa: ARG001
) -> ApiResponse[RecipeResponse]:
    """获取菜谱详情。"""
    recipe = await recipe_service.get_recipe_by_id(db, recipe_id)
    return ApiResponse.success(data=recipe)
