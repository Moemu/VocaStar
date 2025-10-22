from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Sequence

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.models.cosplay import CosplaySession, SessionState
from app.models.user import User
from app.repositories.cosplay import CosplayRepository
from app.schemas.cosplay import (
    CosplayAbilityDescriptor,
    CosplayChoiceRequest,
    CosplayChoiceResponse,
    CosplayEvaluationRule,
    CosplayHistoryRecord,
    CosplayOptionDefinition,
    CosplayOptionView,
    CosplayReportPayload,
    CosplaySceneDefinition,
    CosplaySceneView,
    CosplayScriptContent,
    CosplayScriptDetail,
    CosplayScriptDetailResponse,
    CosplayScriptSummary,
    CosplaySessionListResponse,
    CosplaySessionResumeRequest,
    CosplaySessionState,
    CosplaySessionStateResponse,
)

DEFAULT_BASE_SCORE = 50
DEFAULT_POINT_STEP = 10


class CosplayService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = CosplayRepository(session)

    async def list_scripts(self) -> CosplaySessionListResponse:
        """Return all available cosplay scripts with summary metadata."""
        scripts = await self.repo.list_scripts()
        summaries: list[CosplayScriptSummary] = []
        for script in scripts:
            content = self._parse_content(script.content)
            summaries.append(
                CosplayScriptSummary(
                    id=script.id,
                    title=script.title,
                    summary=content.summary,
                    setting=content.setting,
                    total_scenes=len(content.scenes),
                    updated_at=script.updated_at,
                )
            )
        return CosplaySessionListResponse(scripts=summaries)

    async def get_script_detail(self, script_id: int) -> CosplayScriptDetailResponse:
        """Fetch a full script definition for the given identifier."""
        script = await self.repo.get_script_by_id(script_id)
        if not script:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="剧本不存在")
        content = self._parse_content(script.content)
        detail = CosplayScriptDetail(
            id=script.id,
            title=script.title,
            summary=content.summary,
            setting=content.setting,
            abilities=content.abilities,
            total_scenes=len(content.scenes),
            updated_at=script.updated_at,
        )
        return CosplayScriptDetailResponse(script=detail)

    async def start_session(
        self,
        *,
        script_id: int,
        user: User,
        request: CosplaySessionResumeRequest | None,
    ) -> CosplaySessionStateResponse:
        """Create a new session or resume the latest in-progress session for the script."""
        script = await self.repo.get_script_by_id(script_id)
        if not script:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="剧本不存在")
        content = self._parse_content(script.content)
        resume_existing = True if request is None else request.resume

        if resume_existing:
            existing = await self.repo.get_active_session(user.id, script.id)
            if existing:
                state = self._build_state_payload(existing, content, script.title)
                return CosplaySessionStateResponse(state=state)

        initial_state_payload = self._build_initial_payload(content)
        session_record = await self.repo.create_session(
            user_id=user.id,
            script_id=script.id,
            state_payload=initial_state_payload,
        )
        await self.session.commit()
        await self.session.refresh(session_record, attribute_names=["report"])
        state = self._build_state_payload(session_record, content, script.title)
        return CosplaySessionStateResponse(state=state)

    async def get_session_state(self, *, session_id: int, user: User) -> CosplaySessionStateResponse:
        """Return the latest persisted state for a session owned by the user."""
        record = await self.repo.get_session_by_id(session_id)
        if not record or record.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
        script = await self.repo.get_script_by_id(record.script_id)
        if not script:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="剧本不存在")
        content = self._parse_content(script.content)
        state = self._build_state_payload(record, content, script.title)
        return CosplaySessionStateResponse(state=state)

    async def choose_option(
        self,
        *,
        session_id: int,
        user: User,
        request: CosplayChoiceRequest,
    ) -> CosplayChoiceResponse:
        """Apply the selected option to the current scene and advance the session."""
        record = await self.repo.get_session_by_id(session_id)
        if not record or record.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
        if record.state != SessionState.in_progress:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="剧本已完成或已终止")

        script = await self.repo.get_script_by_id(record.script_id)
        if not script:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="剧本不存在")
        content = self._parse_content(script.content)

        state_payload = self._normalize_state(record.state_payload, content)
        scene_list = list(content.scenes.values())
        current_index = state_payload["current_scene_index"]
        total_scenes = len(scene_list)

        if current_index >= total_scenes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="剧本流程已结束")

        scene_def = scene_list[current_index]
        option_def = self._find_option(scene_def, request.option_id)
        if option_def is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="选项不存在")

        previous_scores = state_payload["scores"].copy()
        updated_scores, score_changes = self._apply_effects(
            previous_scores,
            option_def,
            abilities=content.abilities,
            point_step=content.point_step,
            base_score=content.base_score,
        )

        history_entry = CosplayHistoryRecord(scene_id=scene_def.id, choice_id=option_def.id)
        state_payload["history"].append(history_entry.model_dump())
        state_payload["scores"] = updated_scores
        state_payload["current_scene_index"] = current_index + 1

        record.state_payload = deepcopy(state_payload)
        flag_modified(record, "state_payload")
        record.progress = self._calculate_progress(state_payload["current_scene_index"], total_scenes)

        if state_payload["current_scene_index"] >= total_scenes:
            record.state = SessionState.completed
            record.finished_at = datetime.now(timezone.utc)
            await self._ensure_report(record, content, state_payload)

        await self.session.commit()
        await self.session.refresh(record, attribute_names=["report"])

        next_state = self._build_state_payload(record, content, script.title)

        return CosplayChoiceResponse(
            outcome=option_def.outcome,
            score_changes=score_changes,
            current_scores=updated_scores,
            next_scene=next_state,
        )

    async def get_report(self, *, session_id: int, user: User) -> CosplayReportPayload:
        """Return the final report for a completed session, generating it if needed."""
        record = await self.repo.get_session_by_id(session_id)
        if not record or record.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
        if record.state != SessionState.completed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="会话尚未完成")
        if record.report is None:
            script = await self.repo.get_script_by_id(record.script_id)
            if not script:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="剧本不存在")
            content = self._parse_content(script.content)
            normalized_state = self._normalize_state(record.state_payload, content)
            report = await self._ensure_report(record, content, normalized_state)
            await self.session.commit()
            return report

        return CosplayReportPayload.model_validate(record.report.result_json)

    def _parse_content(self, content_data: dict[str, Any] | None) -> CosplayScriptContent:
        if not content_data:
            raise ValueError("剧本内容为空")
        try:
            return CosplayScriptContent.model_validate(content_data)
        except ValidationError as e:
            # 尝试对旧版/不规范内容进行兼容性规整后再校验
            try:
                coerced = self._coerce_legacy_content(content_data)
                return CosplayScriptContent.model_validate(coerced)
            except Exception:
                raise ValueError(f"剧本内容格式错误: {e}") from e

    def _coerce_legacy_content(self, data: dict[str, Any]) -> dict[str, Any]:
        """将旧版或不规范的剧本内容转换为当前 schema 期望的结构。

        处理要点：
        - scenes: 允许 list，转换为以 id 为键的 dict
        - option.description -> option.outcome
        - 缺失的 effects 补为空 dict
        - 缺失的 initial_scores：按 abilities 生成默认初始分（base_score 或 DEFAULT_BASE_SCORE）
        - 缺失的 evaluations：补为空列表
        - 缺失的 is_end：默认为 False
        """
        payload = deepcopy(data)

        # 1) scenes 列表转字典，并规整 option 字段
        scenes = payload.get("scenes")
        if isinstance(scenes, list):
            scenes_dict: dict[str, Any] = {}
            for scene in scenes:
                if not isinstance(scene, dict):
                    continue
                scene_id = scene.get("id")
                if not scene_id:
                    continue
                options = []
                for opt in scene.get("options", []) or []:
                    if not isinstance(opt, dict):
                        continue
                    # 兼容旧字段 description -> outcome
                    outcome = opt.get("outcome")
                    if outcome is None and "description" in opt:
                        outcome = opt.get("description")
                    options.append(
                        {
                            "id": opt.get("id"),
                            "text": opt.get("text"),
                            "outcome": outcome or "",
                            "effects": opt.get("effects") or {},
                        }
                    )
                # 兼容旧字段 narrative/narration -> text；text 为空则退回 title
                raw_text = scene.get("text")
                if not raw_text or (isinstance(raw_text, str) and not raw_text.strip()):
                    raw_text = scene.get("narrative") or scene.get("narration")
                if not raw_text or (isinstance(raw_text, str) and not raw_text.strip()):
                    raw_text = scene.get("title", "")
                scenes_dict[str(scene_id)] = {
                    "id": scene.get("id"),
                    "title": scene.get("title", ""),
                    "text": raw_text or "",
                    "options": options,
                    "is_end": bool(scene.get("is_end", False)),
                }
            payload["scenes"] = scenes_dict

        # 2) 若 initial_scores 缺失，则依据 abilities + base_score 填充
        if "initial_scores" not in payload:
            abilities = payload.get("abilities") or []
            base = payload.get("base_score") or DEFAULT_BASE_SCORE
            init_scores: dict[str, int] = {}
            for ab in abilities:
                if isinstance(ab, dict) and ab.get("code"):
                    init_scores[ab["code"]] = int(base)
            payload["initial_scores"] = init_scores

        # 3) evaluations 缺失则补空列表
        if "evaluations" not in payload or payload.get("evaluations") is None:
            payload["evaluations"] = []

        # 4) abilities 缺失则补空列表
        if "abilities" not in payload or payload.get("abilities") is None:
            payload["abilities"] = []

        # 其余字段（summary/setting/base_score/point_step）按原值透传
        return payload

    def _find_option(self, scene_def: CosplaySceneDefinition, option_id: str) -> CosplayOptionDefinition | None:
        """Find a specific option definition within a scene."""
        return next((opt for opt in scene_def.options if opt.id == option_id), None)

    def _build_initial_payload(self, content: CosplayScriptContent) -> dict[str, Any]:
        return {
            "scores": content.initial_scores.copy(),
            "history": [],
            "current_scene_index": 0,
        }

    def _apply_effects(
        self,
        current_scores: dict[str, int],
        option: CosplayOptionDefinition,
        *,
        abilities: list[CosplayAbilityDescriptor],
        point_step: int | None,
        base_score: int | None,
    ) -> tuple[dict[str, int], dict[str, int]]:
        """Apply score changes based on option effects and return new scores and deltas."""
        step = point_step or DEFAULT_POINT_STEP
        score_changes: dict[str, int] = {}
        updated_scores = current_scores.copy()
        ability_codes = {ability.code for ability in abilities}

        for ability_code, points in option.effects.items():
            if ability_code in ability_codes:
                change = points * step
                updated_scores[ability_code] = updated_scores.get(ability_code, 0) + change
                score_changes[ability_code] = change

        return updated_scores, score_changes

    def _calculate_progress(self, current_index: int, total_scenes: int) -> int:
        if total_scenes == 0:
            return 100
        progress = int((current_index / total_scenes) * 100)
        return min(progress, 100)

    def _build_state_payload(
        self,
        record: CosplaySession,
        content: CosplayScriptContent,
        script_title: str,
        override_report: CosplayReportPayload | None = None,
    ) -> CosplaySessionState:
        """Construct the comprehensive session state object from various data sources."""
        state_payload = record.state_payload or {}
        scene_list = list(content.scenes.values())
        total_scenes = len(scene_list)
        current_index = state_payload.get("current_scene_index", 0)

        current_scene_view: CosplaySceneView | None = None
        if current_index < total_scenes:
            scene_def = scene_list[current_index]
            current_scene_view = CosplaySceneView(
                id=scene_def.id,
                title=scene_def.title,
                text=scene_def.text or scene_def.title,
                options=[CosplayOptionView(id=opt.id, text=opt.text) for opt in scene_def.options],
                is_end=scene_def.is_end,
            )

        report_payload: CosplayReportPayload | None = None
        if override_report:
            report_payload = override_report
        elif record.report:
            report_payload = CosplayReportPayload.model_validate(record.report.result_json)

        history_records = [CosplayHistoryRecord.model_validate(h) for h in state_payload.get("history", [])]

        return CosplaySessionState(
            session_id=record.id,
            script_id=record.script_id,
            script_title=script_title,
            setting=content.setting,
            progress=record.progress,
            completed=record.state == SessionState.completed,
            current_scene_index=current_index,
            total_scenes=total_scenes,
            scores=state_payload.get("scores", {}),
            abilities=content.abilities,
            current_scene=current_scene_view,
            history=history_records,
            report=report_payload,
        )

    async def _ensure_report(
        self,
        record: CosplaySession,
        content: CosplayScriptContent,
        state_payload: dict[str, Any],
    ) -> CosplayReportPayload:
        """Generate and save a report if it doesn't exist, then return it."""
        if record.report:
            return CosplayReportPayload.model_validate(record.report.result_json)

        final_scores = state_payload.get("scores", {})
        report_payload = self._build_report_payload(content, final_scores, state_payload.get("history", []))
        await self.repo.create_report(
            session_id=record.id,
            payload=report_payload,
        )
        # Commit here to ensure the report is persisted, as the caller may not always commit.
        await self.session.commit()
        return report_payload
        return report_payload

    def _build_report_payload(
        self,
        content: CosplayScriptContent,
        final_scores: dict[str, int],
        history: list[dict[str, Any]],
    ) -> CosplayReportPayload:
        """Construct the final report content based on scores and evaluation rules."""
        best_route = self._evaluate_best_route(content.evaluations, final_scores)
        history_records = [CosplayHistoryRecord.model_validate(h) for h in history]

        return CosplayReportPayload(
            final_scores=final_scores,
            summary=best_route.summary,
            advice=best_route.advice,
            ability_labels={ability.code: ability.name for ability in content.abilities},
            ability_descriptions={
                ability.code: ability.description for ability in content.abilities if ability.description is not None
            },
            history=history_records,
        )

    def _evaluate_best_route(
        self, evaluations: Sequence[CosplayEvaluationRule], final_scores: dict[str, int]
    ) -> CosplayEvaluationRule:
        """Determine the most fitting evaluation rule based on the final scores."""
        if not evaluations:
            return CosplayEvaluationRule(
                summary="旅程已完成。",
                advice="你已经走完了这段独特的职业道路，希望这段经历能为你带来启发。",
                thresholds={},
            )

        # Find the route with the highest minimum score that is met
        best_route = evaluations[0]
        max_min_score = -1.0

        for route in evaluations:
            min_score_for_route = float("inf")
            possible = True
            for ability, required_score in route.thresholds.items():
                if final_scores.get(ability, 0) < required_score:
                    possible = False
                    break
                min_score_for_route = min(min_score_for_route, final_scores.get(ability, 0))

            if possible and min_score_for_route > max_min_score:
                max_min_score = min_score_for_route
                best_route = route

        return best_route

    def _normalize_state(self, state_payload: dict[str, Any] | None, content: CosplayScriptContent) -> dict[str, Any]:
        """Ensure the state payload is well-formed and contains all necessary keys."""
        if not state_payload:
            return self._build_initial_payload(content)

        # Ensure essential keys exist
        state_payload.setdefault("scores", self._build_initial_payload(content)["scores"])
        state_payload.setdefault("history", [])
        state_payload.setdefault("current_scene_index", 0)
        return state_payload
