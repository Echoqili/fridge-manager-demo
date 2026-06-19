"""购物清单服务层。"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotFoundException
from models.shopping_list import ShoppingListItemModel
from schemas.shopping_list import (
    ShoppingItemCreate,
    ShoppingItemResponse,
    ShoppingItemUpdate,
)

logger = logging.getLogger(__name__)


async def get_shopping_list(db: AsyncSession, user_id: str) -> list[ShoppingItemResponse]:
    """获取用户购物清单（按创建时间排序）。"""
    result = await db.execute(
        select(ShoppingListItemModel)
        .where(ShoppingListItemModel.user_id == user_id)
        .order_by(ShoppingListItemModel.created_at.desc())
    )
    items = result.scalars().all()
    return [ShoppingItemResponse.model_validate(item) for item in items]


async def add_shopping_item(db: AsyncSession, user_id: str, data: ShoppingItemCreate) -> ShoppingItemResponse:
    """添加购物清单条目。"""
    item = ShoppingListItemModel(
        user_id=user_id,
        name=data.name,
        quantity=data.quantity,
        checked=data.checked,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    logger.info("用户 %s 添加购物清单条目: %s", user_id, data.name)
    return ShoppingItemResponse.model_validate(item)


async def batch_add_shopping_items(
    db: AsyncSession, user_id: str, items_data: list[ShoppingItemCreate]
) -> list[ShoppingItemResponse]:
    """批量添加购物清单条目。"""
    new_items: list[ShoppingListItemModel] = []
    for data in items_data:
        item = ShoppingListItemModel(
            user_id=user_id,
            name=data.name,
            quantity=data.quantity,
            checked=data.checked,
        )
        db.add(item)
        new_items.append(item)
    await db.commit()
    for item in new_items:
        await db.refresh(item)
    logger.info("用户 %s 批量添加 %d 条购物清单", user_id, len(items_data))
    return [ShoppingItemResponse.model_validate(item) for item in new_items]


async def update_shopping_item(
    db: AsyncSession, user_id: str, item_id: str, data: ShoppingItemUpdate
) -> ShoppingItemResponse:
    """更新购物清单条目。"""
    result = await db.execute(
        select(ShoppingListItemModel).where(
            ShoppingListItemModel.item_id == item_id,
            ShoppingListItemModel.user_id == user_id,
        )
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise NotFoundException(message="购物清单条目不存在")

    if data.name is not None:
        item.name = data.name
    if data.quantity is not None:
        item.quantity = data.quantity
    if data.checked is not None:
        item.checked = data.checked

    await db.commit()
    await db.refresh(item)
    return ShoppingItemResponse.model_validate(item)


async def delete_shopping_item(db: AsyncSession, user_id: str, item_id: str) -> None:
    """删除购物清单条目。"""
    result = await db.execute(
        select(ShoppingListItemModel).where(
            ShoppingListItemModel.item_id == item_id,
            ShoppingListItemModel.user_id == user_id,
        )
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise NotFoundException(message="购物清单条目不存在")
    await db.delete(item)
    await db.commit()


async def clear_shopping_list(db: AsyncSession, user_id: str) -> int:
    """清空用户购物清单，返回删除条数。"""
    result = await db.execute(select(ShoppingListItemModel).where(ShoppingListItemModel.user_id == user_id))
    items = result.scalars().all()
    count = len(items)
    for item in items:
        await db.delete(item)
    await db.commit()
    logger.info("用户 %s 清空购物清单，删除 %d 条", user_id, count)
    return count
