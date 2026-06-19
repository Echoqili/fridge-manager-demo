"""鲜知 fridge · AI 冰箱管家 后端主入口。"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.exceptions import AppException
from models.database import dispose_db, init_db
from routers import auth, health, ingredients, nutrition, recipes, recognition, shopping_list

# 日志配置
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期：启动时初始化数据库，关闭时释放连接。"""
    logger.info("启动 fridge-manager-backend，环境: %s", settings.ENVIRONMENT)
    await init_db()
    logger.info("数据库初始化完成")
    try:
        yield
    finally:
        await dispose_db()
        logger.info("数据库连接已关闭")


app = FastAPI(
    title="鲜知 fridge · AI 冰箱管家",
    description="智能冰箱食材管理与菜谱推荐后端服务",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
api_prefix = "/api/v1"
app.include_router(health.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)
app.include_router(ingredients.router, prefix=api_prefix)
app.include_router(recipes.router, prefix=api_prefix)
app.include_router(recognition.router, prefix=api_prefix)
app.include_router(nutrition.router, prefix=api_prefix)
app.include_router(shopping_list.router, prefix=api_prefix)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """统一应用异常处理。"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """未捕获异常兜底处理。"""
    logger.exception("未处理的异常: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "code": settings.CODE_SERVER_ERROR,
            "message": "服务器内部错误",
            "details": {},
        },
    )


@app.get("/")
async def root() -> dict:
    """根路径欢迎信息。"""
    return {"service": "鲜知 fridge · AI 冰箱管家", "version": "0.1.0", "docs": "/docs"}
