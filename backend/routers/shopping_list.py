"""购物清单路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from models.database import get_db
from models.user import UserModel
from schemas.common import ApiResponse
from schemas.shopping_list import (
    ShoppingItemBatchCreate,
    ShoppingItemCreate,
    ShoppingItemResponse,
    ShoppingItemUpdate,
)
from services import shopping_list_service

router = APIRouter(prefix="/shopping-list", tags=["购物清单"])


@router.get("", response_model=ApiResponse[list[ShoppingItemResponse]])
async def get_list(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[ShoppingItemResponse]]:
    """获取当前用户购物清单。"""
    items = await shopping_list_service.get_shopping_list(db, current_user.user_id)
    return ApiResponse.success(data=items)


@router.post("", response_model=ApiResponse[ShoppingItemResponse])
async def add_item(
    item: ShoppingItemCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ShoppingItemResponse]:
    """添加购物清单条目。"""
    created = await shopping_list_service.add_shopping_item(db, current_user.user_id, item)
    return ApiResponse.success(data=created, message="已添加到购物清单")


@router.post("/batch", response_model=ApiResponse[list[ShoppingItemResponse]])
async def batch_add_items(
    body: ShoppingItemBatchCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[ShoppingItemResponse]]:
    """批量添加购物清单条目。"""
    created = await shopping_list_service.batch_add_shopping_items(db, current_user.user_id, body.items)
    return ApiResponse.success(data=created, message=f"已添加 {len(created)} 条")


@router.put("/{item_id}", response_model=ApiResponse[ShoppingItemResponse])
async def update_item(
    item_id: str,
    item: ShoppingItemUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ShoppingItemResponse]:
    """更新购物清单条目（勾选/改名/改数量）。"""
    updated = await shopping_list_service.update_shopping_item(db, current_user.user_id, item_id, item)
    return ApiResponse.success(data=updated)


@router.delete("/{item_id}", response_model=ApiResponse[None])
async def delete_item(
    item_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    """删除购物清单条目。"""
    await shopping_list_service.delete_shopping_item(db, current_user.user_id, item_id)
    return ApiResponse.success(message="已删除")


@router.delete("", response_model=ApiResponse[dict])
async def clear_list(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    """清空购物清单。"""
    count = await shopping_list_service.clear_shopping_list(db, current_user.user_id)
    return ApiResponse.success(data={"deleted": count}, message=f"已清空 {count} 条")
