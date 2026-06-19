"""购物清单 Schema。"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ShoppingItemCreate(BaseModel):
    """创建购物清单条目。"""

    name: str = Field(..., min_length=1, max_length=128, description="食材名称")
    quantity: str = Field(default="1个", max_length=64, description="数量")
    checked: bool = Field(default=False, description="是否已勾选")


class ShoppingItemUpdate(BaseModel):
    """更新购物清单条目。"""

    name: str | None = Field(default=None, min_length=1, max_length=128)
    quantity: str | None = Field(default=None, max_length=64)
    checked: bool | None = Field(default=None)


class ShoppingItemBatchCreate(BaseModel):
    """批量创建购物清单条目。"""

    items: list[ShoppingItemCreate] = Field(..., min_length=1, description="条目列表")


class ShoppingItemResponse(BaseModel):
    """购物清单条目响应。"""

    item_id: str
    name: str
    quantity: str
    checked: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ShoppingListResponse(BaseModel):
    """购物清单整体响应。"""

    items: list[ShoppingItemResponse] = Field(default_factory=list)
    total: int = 0
