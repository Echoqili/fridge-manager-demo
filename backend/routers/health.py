"""健康检查路由。"""

from __future__ import annotations

from fastapi import APIRouter

from schemas.common import ApiResponse

router = APIRouter()


@router.get("/health", response_model=ApiResponse[dict])
async def health_check() -> ApiResponse[dict]:
    """健康检查接口。"""
    return ApiResponse.success(data={"status": "ok", "service": "fridge-manager-backend"})
