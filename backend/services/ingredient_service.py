"""食材服务层：CRUD 与临期查询。"""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotFoundException, ValidationException
from models.ingredient import IngredientModel
from schemas.ingredient import IngredientCreate, IngredientUpdate


async def create_ingredient(db: AsyncSession, user_id: str, data: IngredientCreate) -> IngredientModel:
    """创建食材。"""
    ingredient = IngredientModel(
        user_id=user_id,
        name=data.name,
        category=data.category,
        quantity=data.quantity,
        unit=data.unit,
        storage_location=data.storage_location,
        purchase_date=data.purchase_date,
        expiry_date=data.expiry_date,
        image_url=data.image_url,
    )
    db.add(ingredient)
    await db.commit()
    await db.refresh(ingredient)
    return ingredient


async def get_ingredients_by_user(
    db: AsyncSession,
    user_id: str,
    category: str | None = None,
    storage_location: str | None = None,
) -> list[IngredientModel]:
    """获取用户的所有食材，可按分类与存储位置过滤。"""
    stmt = select(IngredientModel).where(IngredientModel.user_id == user_id)
    if category:
        stmt = stmt.where(IngredientModel.category == category)
    if storage_location:
        stmt = stmt.where(IngredientModel.storage_location == storage_location)
    stmt = stmt.order_by(IngredientModel.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_ingredient_by_id(db: AsyncSession, ingredient_id: str, user_id: str) -> IngredientModel:
    """根据 ID 获取食材，校验归属。"""
    result = await db.execute(
        select(IngredientModel).where(
            IngredientModel.ingredient_id == ingredient_id,
            IngredientModel.user_id == user_id,
        )
    )
    ingredient = result.scalar_one_or_none()
    if ingredient is None:
        raise NotFoundException(message="食材不存在")
    return ingredient


async def update_ingredient(
    db: AsyncSession, ingredient_id: str, user_id: str, data: IngredientUpdate
) -> IngredientModel:
    """更新食材。"""
    ingredient = await get_ingredient_by_id(db, ingredient_id, user_id)
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise ValidationException(message="未提供任何更新字段")
    for key, value in update_data.items():
        setattr(ingredient, key, value)
    await db.commit()
    await db.refresh(ingredient)
    return ingredient


async def delete_ingredient(db: AsyncSession, ingredient_id: str, user_id: str) -> None:
    """删除食材。"""
    ingredient = await get_ingredient_by_id(db, ingredient_id, user_id)
    await db.delete(ingredient)
    await db.commit()


async def get_expiring_ingredients(db: AsyncSession, user_id: str, days: int = 3) -> list[IngredientModel]:
    """获取即将过期（默认 3 天内）的食材。"""
    today = date.today()
    deadline = today + timedelta(days=days)
    result = await db.execute(
        select(IngredientModel)
        .where(
            IngredientModel.user_id == user_id,
            IngredientModel.expiry_date.is_not(None),
            IngredientModel.expiry_date <= deadline,
        )
        .order_by(IngredientModel.expiry_date.asc())
    )
    return list(result.scalars().all())


async def delete_all_ingredients_by_user(db: AsyncSession, user_id: str) -> int:
    """删除用户的所有食材（测试辅助）。"""
    result = await db.execute(delete(IngredientModel).where(IngredientModel.user_id == user_id))
    await db.commit()
    return result.rowcount or 0
