"""食材路由：CRUD 与临期查询。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from models.database import get_db
from models.user import UserModel
from schemas.common import ApiResponse
from schemas.ingredient import (
    IngredientCreate,
    IngredientListResponse,
    IngredientResponse,
    IngredientUpdate,
)
from services import ingredient_service

router = APIRouter(prefix="/ingredients", tags=["食材管理"])


@router.get("", response_model=ApiResponse[IngredientListResponse])
async def list_ingredients(
    category: str | None = Query(default=None, description="分类过滤"),
    storage_location: str | None = Query(default=None, description="存储位置过滤"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> ApiResponse[IngredientListResponse]:
    """获取当前用户的食材列表。"""
    items = await ingredient_service.get_ingredients_by_user(
        db, current_user.user_id, category=category, storage_location=storage_location
    )
    data = IngredientListResponse(
        items=[IngredientResponse.model_validate(item) for item in items],
        total=len(items),
    )
    return ApiResponse.success(data=data)


@router.post("", response_model=ApiResponse[IngredientResponse])
async def create_ingredient(
    payload: IngredientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> ApiResponse[IngredientResponse]:
    """创建食材。"""
    ingredient = await ingredient_service.create_ingredient(db, current_user.user_id, payload)
    return ApiResponse.success(data=IngredientResponse.model_validate(ingredient))


@router.put("/{ingredient_id}", response_model=ApiResponse[IngredientResponse])
async def update_ingredient(
    ingredient_id: str,
    payload: IngredientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> ApiResponse[IngredientResponse]:
    """更新食材。"""
    ingredient = await ingredient_service.update_ingredient(db, ingredient_id, current_user.user_id, payload)
    return ApiResponse.success(data=IngredientResponse.model_validate(ingredient))


@router.delete("/{ingredient_id}", response_model=ApiResponse[dict])
async def delete_ingredient(
    ingredient_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> ApiResponse[dict]:
    """删除食材。"""
    await ingredient_service.delete_ingredient(db, ingredient_id, current_user.user_id)
    return ApiResponse.success(data={"ingredient_id": ingredient_id})


@router.get("/expiring", response_model=ApiResponse[IngredientListResponse])
async def list_expiring_ingredients(
    days: int = Query(default=3, ge=1, le=30, description="几天内过期"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> ApiResponse[IngredientListResponse]:
    """获取即将过期的食材。"""
    items = await ingredient_service.get_expiring_ingredients(db, current_user.user_id, days=days)
    data = IngredientListResponse(
        items=[IngredientResponse.model_validate(item) for item in items],
        total=len(items),
    )
    return ApiResponse.success(data=data)
