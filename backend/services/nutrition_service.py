"""营养分析服务：按分类统计食材并生成建议。"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.ingredient import IngredientModel

logger = logging.getLogger(__name__)


# 分类中文名映射
CATEGORY_LABELS: dict[str, str] = {
    "vegetable": "蔬菜",
    "meat": "肉类",
    "dairy": "蛋奶",
    "staple": "主食",
    "fruit": "水果",
    "other": "其他",
}


def _build_advice(summary: dict[str, int]) -> list[str]:
    """根据分类统计生成简单的饮食建议。"""
    advice: list[str] = []
    vegetable = summary.get("vegetable", 0)
    meat = summary.get("meat", 0)
    dairy = summary.get("dairy", 0)
    staple = summary.get("staple", 0)
    fruit = summary.get("fruit", 0)

    if vegetable < 2:
        advice.append("蔬菜种类偏少，建议补充绿叶蔬菜以均衡营养。")
    if meat == 0:
        advice.append("暂无肉类食材，可适当补充优质蛋白。")
    if dairy == 0:
        advice.append("蛋奶类不足，建议补充牛奶或鸡蛋。")
    if staple == 0:
        advice.append("缺少主食，建议储备米面等碳水化合物。")
    if fruit == 0:
        advice.append("水果种类为空，可增加水果摄入补充维生素。")
    if not advice:
        advice.append("食材结构较为均衡，请继续保持！")
    return advice


async def get_nutrition_summary(db: AsyncSession, user_id: str) -> dict[str, Any]:
    """按分类统计用户食材数量，生成营养建议。"""
    result = await db.execute(
        select(IngredientModel.category, func.count(IngredientModel.ingredient_id))
        .where(IngredientModel.user_id == user_id)
        .group_by(IngredientModel.category)
    )
    rows = result.all()

    # 原始分类统计
    raw_summary: dict[str, int] = {row[0]: row[1] for row in rows}
    # 补全所有分类
    summary: dict[str, int] = {cat: raw_summary.get(cat, 0) for cat in CATEGORY_LABELS}

    total = sum(summary.values())

    # 带中文名的统计
    labeled: list[dict[str, Any]] = [
        {"category": cat, "label": CATEGORY_LABELS[cat], "count": cnt} for cat, cnt in summary.items()
    ]

    advice = _build_advice(summary)

    return {
        "total": total,
        "by_category": labeled,
        "advice": advice,
    }
