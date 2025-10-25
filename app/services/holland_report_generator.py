from __future__ import annotations

import asyncio
import json
import textwrap
from typing import Optional

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models.quiz import QuizSubmission, UserProfile
from app.models.user import User
from app.schemas.quiz import HollandReport, QuizProfileResponse, QuizReportData
from app.services.llm_service import LLMService
from app.services.quiz_constants import (
    DIMENSION_LABELS,
    DIMENSION_PRIORITY,
    MAX_RECOMMENDATIONS,
)

LLM_SYSTEM_PROMPT = (
    "你是一名资深职业规划师，需要根据霍兰德职业兴趣测评结果，为中文用户撰写结构化的个性化测评总结。"
    "请使用积极、务实的语气，以简体中文输出，严格遵循提供的 Pydantic 模型结构。"
)

LLM_MAX_TOKENS = 1200
LLM_TEMPERATURE = 0.35
LLM_MAX_RETRIES = 3
LLM_RETRY_DELAY_SECONDS = 1.5


class HollandReportGenerator:
    """负责调用 LLM 生成 HollandReport 的服务。"""

    def __init__(self, *, llm_service: Optional[LLMService] = None) -> None:
        self._llm_service = llm_service or LLMService()
        self._llm_disabled = False

    async def generate(
        self,
        *,
        session: AsyncSession,
        submission: QuizSubmission,
        report_data: QuizReportData,
    ) -> Optional[HollandReport]:
        if self._llm_disabled:
            return None

        user: Optional[User] = submission.user
        if not user:
            stmt = select(User).where(User.id == submission.user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if not user:
                logger.warning("生成 HollandReport 时找不到用户数据 submission_id=%s", submission.id)
                return None

        profile_payload = await self._load_profile(session=session, user_id=submission.user_id)

        top_recommendations = [
            item.model_dump(mode="json") for item in report_data.recommendations[:MAX_RECOMMENDATIONS]
        ]
        context = {
            "user": {
                "id": user.id,
                "nickname": user.nickname,
                "bio": getattr(user, "bio", None),
            },
            "profile": profile_payload,
            "quiz_result": {
                "holland_code": report_data.holland_code,
                "dimension_scores": report_data.dimension_scores,
                "component_scores": report_data.component_scores,
                "recommendations": top_recommendations,
                "unique_advantage": report_data.unique_advantage,
            },
            "dimension_labels": DIMENSION_LABELS,
            "dimension_priority": DIMENSION_PRIORITY,
        }

        instructions = (
            "请根据以下用户背景和霍兰德测评数据生成结构化报告，严格输出 JSON 字符串，不要包含多余文本或代码块。"
            "JSON 结构必须与下列示例字段完全一致："
            '{"career_directions":[{"career":"...","description":"...","recommended_action":["...","...","..."]},'
            '{"career":"...","description":"...","recommended_action":["...","...","..."]},'
            '{"career":"...","description":"...","recommended_action":["...","...","..."]}],'  # noqa: E501
            '"action_roadmap":{"small_goals":[{"title":"...","content":"..."},'
            '{"title":"...","content":"..."},{"title":"...","content":"..."}],"need_attention":"...","conclusion":"..."}}'  # noqa: E501
            "。"
            "每个 career_directions.description 不超过 100 字，recommended_action 严格输出 3 条，单条不超过 40 字；"
            "small_goals 只输出 3 个，title 不超过 15 字，content 不超过 50 字；need_attention 与 conclusion 各不超过 120 字。"
            "若信息缺失请结合测评数据合理补充，不要输出 null 或空字符串。"
        )

        payload_text = json.dumps(context, ensure_ascii=False, separators=(",", ":"))
        base_prompt = f"{instructions}\n\n测评数据：\n{payload_text}"

        for attempt in range(1, LLM_MAX_RETRIES + 1):
            prompt = (
                base_prompt
                if attempt == 1
                else (
                    f"{base_prompt}\n\n请再次确认仅输出严格符合上述结构的 JSON，"
                    "不要添加额外的说明、注释或 Markdown 包裹。"
                )
            )
            try:
                raw_response = await self._llm_service.generate_chat_completion(
                    message=prompt,
                    system=LLM_SYSTEM_PROMPT,
                    temperature=LLM_TEMPERATURE,
                    max_tokens=LLM_MAX_TOKENS,
                )
            except HTTPException as exc:
                if exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
                    self._llm_disabled = True
                    logger.info("LLM 服务未启用，跳过 HollandReport 生成")
                    return None
                logger.warning(
                    "调用 LLM 生成 HollandReport 失败 submission_id=%s attempt=%s: %s",
                    submission.id,
                    attempt,
                    exc,
                )
                if attempt >= LLM_MAX_RETRIES:
                    return None
                await asyncio.sleep(LLM_RETRY_DELAY_SECONDS)
                continue
            except Exception as exc:  # pragma: no cover - LLM 未知异常兜底
                logger.warning(
                    "生成 HollandReport 时出现异常 submission_id=%s attempt=%s: %s",
                    submission.id,
                    attempt,
                    exc,
                )
                if attempt >= LLM_MAX_RETRIES:
                    return None
                await asyncio.sleep(LLM_RETRY_DELAY_SECONDS)
                continue

            json_text = self._extract_json(raw_response)
            if json_text is None:
                preview = textwrap.shorten(raw_response, width=180, placeholder="...")
                logger.warning(
                    "LLM 返回内容无法提取 JSON submission_id=%s attempt=%s preview=%s",
                    submission.id,
                    attempt,
                    preview,
                )
                if attempt >= LLM_MAX_RETRIES:
                    return None
                await asyncio.sleep(LLM_RETRY_DELAY_SECONDS)
                continue

            try:
                payload = json.loads(json_text)
            except json.JSONDecodeError as exc:
                preview = textwrap.shorten(json_text, width=180, placeholder="...")
                logger.warning(
                    "LLM 返回内容无法解析为 JSON submission_id=%s attempt=%s error=%s preview=%s",
                    submission.id,
                    attempt,
                    exc,
                    preview,
                )
                if attempt >= LLM_MAX_RETRIES:
                    return None
                await asyncio.sleep(LLM_RETRY_DELAY_SECONDS)
                continue

            try:
                return HollandReport.model_validate(payload)
            except ValidationError as exc:
                preview = textwrap.shorten(json_text, width=180, placeholder="...")
                logger.warning(
                    "LLM 返回 JSON 不符合 HollandReport 模型 submission_id=%s attempt=%s errors=%s preview=%s",
                    submission.id,
                    attempt,
                    exc,
                    preview,
                )
                if attempt >= LLM_MAX_RETRIES:
                    return None
                await asyncio.sleep(LLM_RETRY_DELAY_SECONDS)
                continue

        return None

    async def _load_profile(self, *, session: AsyncSession, user_id: int) -> Optional[dict]:
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await session.execute(stmt)
        profile = result.scalars().first()
        if not profile:
            return None
        profile_schema = QuizProfileResponse(
            career_stage=profile.career_stage,
            major=profile.major,
            career_confusion=profile.career_confusion,
            short_term_goals=profile.short_term_goals,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
        return profile_schema.model_dump(mode="json")

    @staticmethod
    def _extract_json(raw_text: str) -> Optional[str]:
        content = raw_text.strip()
        if not content:
            return None
        if content.startswith("```"):
            # 处理 ```json ... ``` 或 ``` ... ``` 包裹情况
            parts = content.split("\n", 1)
            if len(parts) == 2:
                content = parts[1]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        return content or None
