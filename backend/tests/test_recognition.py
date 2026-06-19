"""图像识别接口测试（mock AI）。"""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from schemas.recognition import RecognitionResult

pytestmark = pytest.mark.asyncio


async def test_recognize_fallback(auth_client):
    """测试 AI 不可用时降级返回预设列表。"""
    # 模拟 AI 不可用（无 API Key 场景）
    image_bytes = b"fake-image-bytes"
    resp = await auth_client.post(
        "/api/v1/recognition/recognize",
        files={"file": ("test.jpg", image_bytes, "image/jpeg")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert data["source"] == "fallback"
    assert len(data["results"]) > 0
    assert data["message"] is not None


async def test_recognize_with_mocked_ai(auth_client):
    """测试 mock AI 返回识别结果。"""
    mock_results = [
        RecognitionResult(name="西红柿", category="vegetable", confidence=0.95, quantity=2.0),
        RecognitionResult(name="鸡蛋", category="dairy", confidence=0.88, quantity=3.0),
    ]
    with patch(
        "services.recognition_service._recognize_with_openai",
        new_callable=AsyncMock,
        return_value=mock_results,
    ):
        resp = await auth_client.post(
            "/api/v1/recognition/recognize",
            files={"file": ("test.jpg", b"fake-image", "image/jpeg")},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert data["source"] == "ai"
    assert len(data["results"]) == 2
    assert data["results"][0]["name"] == "西红柿"


async def test_recognize_with_zhipu(auth_client):
    """测试智谱 GLM-4V 降级识别。"""
    mock_zhipu_response = {
        "choices": [{"message": {"content": '[{"name":"黄瓜","category":"vegetable","confidence":0.9,"quantity":1}]'}}]
    }
    mock_resp = Mock()
    mock_resp.raise_for_status = Mock()
    mock_resp.json = Mock(return_value=mock_zhipu_response)

    with (
        patch(
            "services.recognition_service.settings.OPENAI_API_KEY",
            "",
        ),
        patch(
            "services.recognition_service.settings.ZHIPU_API_KEY",
            "test-zhipu-key",
        ),
        patch("httpx.AsyncClient") as mock_client_class,
    ):
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        resp = await auth_client.post(
            "/api/v1/recognition/recognize",
            files={"file": ("test.jpg", b"fake-image", "image/jpeg")},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert data["source"] == "ai"
    assert len(data["results"]) == 1
    assert data["results"][0]["name"] == "黄瓜"


async def test_recognize_zhipu_fallback_to_preset(auth_client):
    """测试智谱 API 异常时降级到预设列表。"""
    with (
        patch(
            "services.recognition_service.settings.OPENAI_API_KEY",
            "",
        ),
        patch(
            "services.recognition_service.settings.ZHIPU_API_KEY",
            "test-zhipu-key",
        ),
        patch("httpx.AsyncClient") as mock_client_class,
    ):
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=Exception("network error"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        resp = await auth_client.post(
            "/api/v1/recognition/recognize",
            files={"file": ("test.jpg", b"fake-image", "image/jpeg")},
        )
    assert resp.status_code == 200
    body = resp.json()
    data = body["data"]
    assert data["source"] == "fallback"
    assert len(data["results"]) > 0


async def test_recognize_requires_auth(async_client):
    """测试无认证访问识别接口被拒。"""
    resp = await async_client.post(
        "/api/v1/recognition/recognize",
        files={"file": ("test.jpg", b"fake", "image/jpeg")},
    )
    assert resp.status_code == 401


async def test_recognition_result_structure(auth_client):
    """测试识别结果结构。"""
    resp = await auth_client.post(
        "/api/v1/recognition/recognize",
        files={"file": ("test.jpg", b"fake-image", "image/jpeg")},
    )
    body = resp.json()
    result = body["data"]["results"][0]
    assert "name" in result
    assert "category" in result
    assert "confidence" in result
    assert 0 <= result["confidence"] <= 1
