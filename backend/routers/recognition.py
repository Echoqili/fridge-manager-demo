"""图像识别路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from core.security import get_current_user
from models.user import UserModel
from schemas.common import ApiResponse
from schemas.recognition import RecognitionResponse
from services import recognition_service

router = APIRouter(prefix="/recognition", tags=["图像识别"])


@router.post("/recognize", response_model=ApiResponse[RecognitionResponse])
async def recognize(
    file: UploadFile = File(..., description="食材图片"),
    current_user: UserModel = Depends(get_current_user),  # noqa: ARG001
) -> ApiResponse[RecognitionResponse]:
    """识别图片中的食材。

    优先调用 AI（OpenAI GPT-4o / 智谱 GLM-4V），不可用时降级返回预设列表。
    """
    image_bytes = await file.read()
    result = await recognition_service.recognize_image(image_bytes)
    return ApiResponse.success(data=result)
