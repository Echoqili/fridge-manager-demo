"""认证相关 Schema。"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """登录请求。"""

    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., min_length=6, max_length=64, description="密码")


class RegisterRequest(BaseModel):
    """注册请求。"""

    username: str = Field(..., min_length=3, max_length=64, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=64, description="密码")


class UserResponse(BaseModel):
    """用户信息响应。"""

    user_id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Token 响应。"""

    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse | None = Field(default=None, description="用户信息")


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求。"""

    refresh_token: str = Field(..., description="刷新令牌")
