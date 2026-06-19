"""菜谱相关 Schema。"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class RecipeStep(BaseModel):
    """菜谱步骤。"""

    step: int = Field(..., description="步骤序号")
    description: str = Field(..., description="步骤描述")


class RecipeIngredient(BaseModel):
    """菜谱所需食材。"""

    ingredient_name: str = Field(..., description="食材名称")
    amount: str | None = Field(default=None, description="用量")
    is_required: bool = Field(default=True, description="是否必需")


class RecipeResponse(BaseModel):
    """菜谱响应。"""

    recipe_id: str
    name: str
    description: str | None = None
    cook_time: int | None = None
    calories: float | None = None
    servings: int | None = None
    steps: list[RecipeStep] | None = None
    image_url: str | None = None
    source: Literal["ai", "local"] = "local"
    ingredients: list[RecipeIngredient] = Field(default_factory=list)
    match_count: int | None = Field(default=None, description="已匹配的食材数量")
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class RecipeRecommendRequest(BaseModel):
    """菜谱推荐请求。"""

    user_ingredients: list[str] | None = Field(default=None, description="指定食材列表，为空则使用库存")
    limit: int = Field(default=5, ge=1, le=20, description="推荐数量")
