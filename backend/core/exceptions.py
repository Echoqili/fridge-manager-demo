"""自定义异常类。"""

from __future__ import annotations

from typing import Any


class AppException(Exception):  # noqa: N818
    """应用基础异常类。"""

    def __init__(
        self,
        message: str = "服务器内部错误",
        code: int = 50001,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundException(AppException):
    """资源不存在异常。"""

    def __init__(self, message: str = "资源不存在", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code=40401, status_code=404, details=details)


class ValidationException(AppException):
    """参数校验异常。"""

    def __init__(self, message: str = "参数错误", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code=40001, status_code=400, details=details)


class AuthenticationException(AppException):
    """认证异常。"""

    def __init__(self, message: str = "认证失败", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code=40101, status_code=401, details=details)
