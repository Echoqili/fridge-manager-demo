"""安全模块：JWT 双 Token 与密码哈希。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from models.database import get_db
from models.user import UserModel

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 安全方案
security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """对明文密码进行 bcrypt 哈希。"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码与哈希值是否匹配。"""
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(data: dict[str, Any], expires_delta: timedelta, token_type: str) -> str:
    """生成 JWT Token 的内部方法。"""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    to_encode.update({"exp": now + expires_delta, "iat": now, "type": token_type})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str | UUID) -> str:
    """创建访问令牌（短期，默认 15 分钟）。"""
    return _create_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        token_type="access",  # noqa: S106
    )


def create_refresh_token(user_id: str | UUID) -> str:
    """创建刷新令牌（长期，默认 7 天）。"""
    return _create_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS),
        token_type="refresh",  # noqa: S106
    )


def create_token_pair(user_id: str | UUID) -> tuple[str, str]:
    """创建访问令牌与刷新令牌对。"""
    return create_access_token(user_id), create_refresh_token(user_id)


def decode_token(token: str) -> dict[str, Any]:
    """解码并验证 JWT Token，失败抛出 JWTError。"""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    """从请求头解析 JWT 并返回当前用户。"""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": settings.CODE_AUTH_ERROR, "message": "未提供认证凭据"},
        )

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": settings.CODE_AUTH_ERROR, "message": "无效的认证令牌"},
        ) from None

    token_type = payload.get("type")
    if token_type != "access":  # noqa: S105
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": settings.CODE_AUTH_ERROR, "message": "令牌类型错误"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": settings.CODE_AUTH_ERROR, "message": "令牌缺少用户信息"},
        )

    result = await db.execute(select(UserModel).where(UserModel.user_id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": settings.CODE_AUTH_ERROR, "message": "用户不存在或已被禁用"},
        )
    return user
