"""图像识别相关 Schema。"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RecognitionResult(BaseModel):
    """单个识别结果。"""

    name: str = Field(..., description="食材名称")
    category: str = Field(default="other", description="分类")
    confidence: float = Field(default=0.0, ge=0, le=1, description="置信度")
    quantity: float | None = Field(default=None, description="估计数量")


class RecognitionResponse(BaseModel):
    """识别响应。"""

    results: list[RecognitionResult] = Field(default_factory=list, description="识别结果列表")
    source: Literal["ai", "fallback"] = "fallback"
    message: str | None = Field(default=None, description="附加提示信息")
