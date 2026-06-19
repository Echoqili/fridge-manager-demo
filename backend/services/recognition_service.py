"""图像识别服务：调用 OpenAI GPT-4o 或智谱 GLM-4V 识别食材。

AI 不可用时降级返回预设食材关键词库。
"""

from __future__ import annotations

import base64
import json
import logging

import httpx

from core.config import settings
from schemas.recognition import RecognitionResponse, RecognitionResult

logger = logging.getLogger(__name__)


# 本地预设食材关键词库（降级使用）
FALLBACK_INGREDIENTS: list[RecognitionResult] = [
    RecognitionResult(name="西红柿", category="vegetable", confidence=0.6),
    RecognitionResult(name="鸡蛋", category="dairy", confidence=0.6),
    RecognitionResult(name="土豆", category="vegetable", confidence=0.6),
    RecognitionResult(name="牛奶", category="dairy", confidence=0.6),
    RecognitionResult(name="胡萝卜", category="vegetable", confidence=0.6),
    RecognitionResult(name="西兰花", category="vegetable", confidence=0.6),
    RecognitionResult(name="猪肉", category="meat", confidence=0.6),
    RecognitionResult(name="牛肉", category="meat", confidence=0.6),
]


def _encode_image(image_bytes: bytes) -> str:
    """将图片字节编码为 base64 字符串。"""
    return base64.b64encode(image_bytes).decode("utf-8")


def _build_openai_prompt() -> str:
    """构造 GPT-4o 识别提示词。"""
    return (
        "请识别图片中的食材，返回 JSON 数组，每个元素包含字段："
        "name(食材名称)、category(分类:vegetable/meat/dairy/staple/fruit/other)、"
        "confidence(置信度0-1)、quantity(估计数量，可选)。"
        "仅返回 JSON，不要其他文字。"
    )


def _clean_json_content(content: str) -> str:
    """清理 LLM 返回内容中的 Markdown 代码块标记。"""
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
    if content.endswith("```"):
        content = content.rsplit("\n", 1)[0]
    return content.strip()


async def _recognize_with_openai(image_bytes: bytes) -> list[RecognitionResult] | None:
    """使用 OpenAI GPT-4o 识别食材。"""
    if not settings.OPENAI_API_KEY:
        return None
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        base64_image = _encode_image(image_bytes)

        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": _build_openai_prompt()},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ],
            max_tokens=500,
        )
        content = response.choices[0].message.content or ""
        content = _clean_json_content(content)
        data = json.loads(content)
        results: list[RecognitionResult] = []
        for item in data:
            results.append(
                RecognitionResult(
                    name=item.get("name", "未知"),
                    category=item.get("category", "other"),
                    confidence=float(item.get("confidence", 0.5)),
                    quantity=item.get("quantity"),
                )
            )
        return results
    except Exception as exc:  # noqa: BLE001
        logger.warning("OpenAI 识别失败，将降级: %s", exc)
        return None


async def _recognize_with_zhipu(image_bytes: bytes) -> list[RecognitionResult] | None:
    """使用智谱 GLM-4V 识别食材。

    通过智谱开放平台 API 调用 GLM-4V 多模态模型，发送 base64 图片并要求返回 JSON。
    """
    if not settings.ZHIPU_API_KEY:
        return None
    try:
        base64_image = _encode_image(image_bytes)
        payload = {
            "model": settings.ZHIPU_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": _build_openai_prompt()},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ],
            "max_tokens": 500,
            "temperature": 0.1,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.ZHIPU_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"] or ""
        content = _clean_json_content(content)
        items = json.loads(content)
        results: list[RecognitionResult] = []
        for item in items:
            results.append(
                RecognitionResult(
                    name=item.get("name", "未知"),
                    category=item.get("category", "other"),
                    confidence=float(item.get("confidence", 0.5)),
                    quantity=item.get("quantity"),
                )
            )
        logger.info("智谱 GLM-4V 识别成功，返回 %d 种食材", len(results))
        return results
    except Exception as exc:  # noqa: BLE001
        logger.warning("智谱 GLM-4V 识别失败，将降级: %s", exc)
        return None


async def recognize_image(image_bytes: bytes) -> RecognitionResponse:
    """识别图片中的食材。

    优先调用 OpenAI GPT-4o，其次智谱 GLM-4V，均不可用时降级返回预设列表。
    """
    # 1. 尝试 OpenAI
    results = await _recognize_with_openai(image_bytes)
    if results is not None:
        return RecognitionResponse(results=results, source="ai", message=None)

    # 2. 尝试智谱
    results = await _recognize_with_zhipu(image_bytes)
    if results is not None:
        return RecognitionResponse(results=results, source="ai", message=None)

    # 3. 降级返回预设列表
    return RecognitionResponse(
        results=FALLBACK_INGREDIENTS,
        source="fallback",
        message="AI 服务不可用，已返回预设食材列表供参考",
    )
