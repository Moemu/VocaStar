from types import SimpleNamespace
from typing import Any, Optional, cast

import pytest
from fastapi import HTTPException
from openai import AsyncOpenAI

from app.services.llm_service import LLMService


class MockChatCompletions:
    def __init__(self, *, content: str = "Hello from mock model") -> None:
        self.content = content
        self.kwargs: Optional[dict[str, Any]] = None

    async def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))])


class MockAsyncOpenAI:
    def __init__(self, *, content: str = "Hello from mock model") -> None:
        self.completions = MockChatCompletions(content=content)
        self.chat = SimpleNamespace(completions=self.completions)


@pytest.mark.asyncio
async def test_generate_chat_completion_success():
    mock_client = MockAsyncOpenAI()
    service = LLMService(
        api_base="http://mock-llm.local/v1",
        api_key="test-key",
        default_model="test-model",
        timeout=5.0,
        client=cast(AsyncOpenAI, mock_client),
    )

    result = await service.generate_chat_completion("Hi")
    assert result == "Hello from mock model"
    assert mock_client.completions.kwargs is not None
    assert mock_client.completions.kwargs["model"] == "test-model"
    assert mock_client.completions.kwargs["messages"][0]["role"] == "user"


@pytest.mark.asyncio
async def test_generate_chat_completion_missing_config():
    service = LLMService(api_base="", api_key="", default_model="", timeout=1)
    with pytest.raises(HTTPException) as exc_info:
        await service.generate_chat_completion("test")
    assert exc_info.value.status_code == 503
