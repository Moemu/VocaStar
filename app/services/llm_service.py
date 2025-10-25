from __future__ import annotations

from typing import Any, Iterable, Optional, Type, TypeVar

from fastapi import HTTPException, status
from openai import AsyncOpenAI, OpenAIError
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from app.core.config import config
from app.core.logger import logger

TModel = TypeVar("TModel", bound=BaseModel)

HistoryChatMessage = list[tuple[str, str]]


class LLMService:
    """提供与 OpenAI 兼容接口交互的封装。"""

    def __init__(
        self,
        *,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[float] = None,
        client: Optional[AsyncOpenAI] = None,
    ) -> None:
        raw_base = api_base or config.llm_api_base_url
        self.api_base = raw_base.rstrip("/") if raw_base else ""
        self.api_key = api_key or config.llm_api_key
        self.default_model = default_model or config.llm_default_model
        self.timeout = timeout or config.llm_request_timeout
        self._client = client or self._get_client()

    def _ensure_configured(self) -> None:
        if not self.api_key:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LLM 服务未启用")
        if not self.default_model:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="默认模型未配置")

    def _get_client(self) -> AsyncOpenAI:
        client_kwargs: dict[str, Any] = {
            "api_key": self.api_key,
            "timeout": self.timeout,
        }
        if self.api_base:
            client_kwargs["base_url"] = self.api_base

        return AsyncOpenAI(**client_kwargs)

    def _build_messages(
        self, prompt: str, history: Optional[HistoryChatMessage] = None, system: Optional[str] = None
    ) -> Iterable[ChatCompletionMessageParam]:
        messages: list[ChatCompletionMessageParam] = []

        if system:
            messages.append({"role": "system", "content": system})

        if history:
            for item in history:
                messages.append({"role": "user", "content": item[0]})
                messages.append({"role": "assistant", "content": item[1]})

        messages.append({"role": "user", "content": prompt})

        return messages

    async def generate_chat_completion(
        self,
        message: str,
        *,
        history: Optional[HistoryChatMessage] = None,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        extra_body: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        调用 LLM 服务生成对话回复

        :raise OpenAIError: OpenAI SDK 内部错误
        :raise RuntimeError: 模型内部相关错误
        """

        self._ensure_configured()

        model = model or self.default_model
        messages = self._build_messages(message, history=history, system=system)

        if stream:
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="暂不支持流式响应")

        try:
            response = await self._client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
                extra_body=extra_body,
            )
        except OpenAIError as exc:
            logger.error("调用 LLM 接口失败: %s", exc)
            raise
        except Exception as exc:  # pragma: no cover - 意外异常兜底
            logger.exception("调用 LLM 接口出现未知异常: ", exc)
            raise

        choices = response.choices
        if not choices:
            logger.warning("LLM 服务返回数据缺少 choices 字段: %s", response)
            raise RuntimeError("LLM 服务返回数据缺少 choices 字段: %s", response)
        message_content = choices[0].message.content

        if not message_content:
            logger.warning("LLM 服务返回内容为空: %s", message_content)
            raise RuntimeError("LLM 服务返回内容为空: %s", message_content)

        return message_content

    async def generate_structured_completion(
        self,
        message: str,
        *,
        response_model: Type[TModel],
        history: Optional[HistoryChatMessage] = None,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        extra_body: Optional[dict[str, Any]] = None,
    ) -> TModel:
        """使用 SDK parse 功能返回结构化 Pydantic 对象。"""

        self._ensure_configured()

        model = model or self.default_model
        messages = list(self._build_messages(message, history=history, system=system))

        try:
            response = await self._client.chat.completions.parse(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_model,
                extra_body=extra_body,
            )
        except OpenAIError as exc:
            logger.error("调用结构化 LLM 接口失败: %s", exc)
            raise
        except Exception as exc:  # pragma: no cover - 意外异常兜底
            logger.exception("调用结构化 LLM 接口出现未知异常: ", exc)
            raise

        choices = response.choices
        if not choices:
            logger.warning("结构化 LLM 返回缺少 choices: %s", response)
            raise RuntimeError("LLM 服务返回数据缺少 choices 字段")

        parsed = getattr(choices[0].message, "parsed", None)
        if parsed is None:
            logger.warning("结构化 LLM 返回内容缺少 parsed 字段: %s", choices[0].message)
            raise RuntimeError("LLM 返回的结构化数据缺失")

        if not isinstance(parsed, response_model):  # type: ignore[arg-type]
            logger.warning("结构化 LLM 返回类型不匹配: %s", parsed)
            raise RuntimeError("LLM 返回的结构化数据类型不匹配")

        return parsed
