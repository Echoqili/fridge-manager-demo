"""食材相关 Schema。"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["vegetable", "meat", "dairy", "staple", "fruit", "other"]
StorageLocation = Literal["fridge", "freezer", "crisper", "pantry"]


class IngredientBase(BaseModel):
    """食材基础字段。"""

    name: str = Field(..., max_length=128, description="食材名称")
    category: Category = Field(default="other", description="分类")
    quantity: float = Field(default=0.0, ge=0, description="数量")
    unit: str = Field(default="个", max_length=16, description="单位")
    storage_location: StorageLocation = Field(default="fridge", description="存储位置")
    purchase_date: date | None = Field(default=None, description="购买日期")
    expiry_date: date | None = Field(default=None, description="过期日期")
    image_url: str | None = Field(default=None, max_length=512, description="图片地址")


class IngredientCreate(IngredientBase):
    """创建食材请求。"""

    pass


class IngredientUpdate(BaseModel):
    """更新食材请求。"""

    name: str | None = Field(default=None, max_length=128)
    category: Category | None = None
    quantity: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=16)
    storage_location: StorageLocation | None = None
    purchase_date: date | None = None
    expiry_date: date | None = None
    image_url: str | None = Field(default=None, max_length=512)


class IngredientResponse(IngredientBase):
    """食材响应。"""

    ingredient_id: str
    user_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class IngredientListResponse(BaseModel):
    """食材列表响应。"""

    items: list[IngredientResponse]
    total: int
