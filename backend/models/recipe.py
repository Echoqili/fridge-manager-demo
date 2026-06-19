"""菜谱模型。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from models.database import Base
from models.user import GUID


class RecipeModel(Base):
    """菜谱表。"""

    __tablename__ = "recipes"

    recipe_id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cook_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    calories: Mapped[float | None] = mapped_column(Float, nullable=True)
    servings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    steps: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source: Mapped[str] = mapped_column(String(16), nullable=False, default="local")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    ingredients: Mapped[list[RecipeIngredientModel]] = relationship(
        "RecipeIngredientModel",
        back_populates="recipe",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class RecipeIngredientModel(Base):
    """菜谱食材关联表。"""

    __tablename__ = "recipe_ingredients"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    recipe_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("recipes.recipe_id", ondelete="CASCADE"), index=True, nullable=False
    )
    ingredient_name: Mapped[str] = mapped_column(String(128), nullable=False)
    amount: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    recipe: Mapped[RecipeModel] = relationship("RecipeModel", back_populates="ingredients")
