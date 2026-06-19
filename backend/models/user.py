"""用户模型。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.sqlite import CHAR
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from models.database import Base


class GUID(TypeDecorator):
    """跨数据库兼容的 UUID 类型，SQLite 使用 CHAR(36)。"""

    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):  # type: ignore[override]
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):  # type: ignore[override]
        if value is not None:
            return str(value)
        return value


class UserModel(Base):
    """用户表。"""

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
