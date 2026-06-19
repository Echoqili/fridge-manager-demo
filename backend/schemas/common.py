"""通用响应模型。"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应模型。"""

    code: int = Field(default=0, description="业务状态码，0 表示成功")
    message: str = Field(default="success", description="提示信息")
    data: T | None = Field(default=None, description="响应数据")

    @classmethod
    def success(cls, data: T = None, message: str = "success") -> ApiResponse[T]:
        """构造成功响应。"""
        return cls(code=0, message=message, data=data)

    @classmethod
    def error(cls, message: str, code: int = 50001, data: T = None) -> ApiResponse[T]:
        """构造失败响应。"""
        return cls(code=code, message=message, data=data)


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型。"""

    items: list[T] = Field(default_factory=list, description="当前页数据")
    total: int = Field(default=0, description="总条数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页条数")
    total_pages: int = Field(default=0, description="总页数")


class ErrorResponse(BaseModel):
    """错误响应模型。"""

    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    details: Any | None = Field(default=None, description="错误详情")


class PaginationParams(BaseModel):
    """分页参数。"""

    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页条数")
