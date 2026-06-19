"""营养分析路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from models.database import get_db
from models.user import UserModel
from schemas.common import ApiResponse
from services import nutrition_service

router = APIRouter(prefix="/nutrition", tags=["营养分析"])


@router.get("/summary", response_model=ApiResponse[dict])
async def nutrition_summary(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> ApiResponse[dict]:
    """获取食材分类统计与营养建议。"""
    summary = await nutrition_service.get_nutrition_summary(db, current_user.user_id)
    return ApiResponse.success(data=summary)
