"""认证路由：注册、登录、刷新、登出、获取当前用户。"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from jose import JWTError
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import AuthenticationException, ValidationException
from core.security import (
    create_token_pair,
    decode_token,
    get_current_user,
    hash_password,
    verify_password,
)
from models.database import get_db
from models.user import UserModel
from schemas.auth import LoginRequest, RefreshTokenRequest, RegisterRequest, TokenResponse, UserResponse
from schemas.common import ApiResponse

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=ApiResponse[UserResponse])
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> ApiResponse[UserResponse]:
    """用户注册。"""
    # 检查用户名或邮箱是否已存在
    result = await db.execute(
        select(UserModel).where(or_(UserModel.username == payload.username, UserModel.email == payload.email))
    )
    if result.scalar_one_or_none() is not None:
        raise ValidationException(message="用户名或邮箱已被注册")

    user = UserModel(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return ApiResponse.success(data=UserResponse.model_validate(user))


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> ApiResponse[TokenResponse]:
    """用户登录，返回双 Token。"""
    result = await db.execute(
        select(UserModel).where(or_(UserModel.username == payload.username, UserModel.email == payload.username))
    )
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise AuthenticationException(message="用户名或密码错误")
    if not user.is_active:
        raise AuthenticationException(message="账号已被禁用")

    access_token, refresh_token = create_token_pair(user.user_id)
    return ApiResponse.success(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )
    )


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)) -> ApiResponse[TokenResponse]:
    """使用刷新令牌换取新的双 Token。"""
    try:
        token_data = decode_token(payload.refresh_token)
    except JWTError:
        raise AuthenticationException(message="刷新令牌无效") from None

    if token_data.get("type") != "refresh":
        raise AuthenticationException(message="令牌类型错误")

    user_id = token_data.get("sub")
    if not user_id:
        raise AuthenticationException(message="令牌缺少用户信息")

    result = await db.execute(select(UserModel).where(UserModel.user_id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise AuthenticationException(message="用户不存在或已被禁用")

    access_token, new_refresh_token = create_token_pair(user.user_id)
    return ApiResponse.success(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            user=UserResponse.model_validate(user),
        )
    )


@router.post("/logout", response_model=ApiResponse[dict])
async def logout() -> ApiResponse[dict]:
    """登出（无状态 JWT，客户端清除令牌即可）。"""
    return ApiResponse.success(data={"message": "已登出"})


@router.get("/me", response_model=ApiResponse[UserResponse])
async def me(current_user: UserModel = Depends(get_current_user)) -> ApiResponse[UserResponse]:
    """获取当前登录用户信息。"""
    return ApiResponse.success(data=UserResponse.model_validate(current_user))
