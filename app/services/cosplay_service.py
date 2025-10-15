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
    ) -> CosplaySessionStateResponse:
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

        normalized_state = self._normalize_state(record.state_payload, content)
        current_index = normalized_state["current_scene_index"]
        total_scenes = len(content.scenes)
        if current_index >= total_scenes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="剧本流程已结束")

        scene = content.scenes[current_index]
        option = self._find_option(scene, request.option_id)
        if option is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="选项不存在")

        updated_scores, delta_points = self._apply_effects(
            normalized_state["scores"],
            option,
            abilities=content.abilities,
            point_step=content.point_step,
            base_score=content.base_score,
        )
        history_entry = self._build_history_entry(
            scene=scene,
            option=option,
            delta_points=delta_points,
            updated_scores=updated_scores,
        )
        normalized_state["history"].append(history_entry)
        normalized_state["scores"] = updated_scores
        normalized_state["current_scene_index"] = current_index + 1

        record.state_payload = deepcopy(normalized_state)
        flag_modified(record, "state_payload")
        record.progress = self._calculate_progress(normalized_state["current_scene_index"], total_scenes)

        report_payload: CosplayReportPayload | None = None
        if normalized_state["current_scene_index"] >= total_scenes:
            record.state = SessionState.completed
            record.finished_at = datetime.now(timezone.utc)
            report_payload = await self._ensure_report(record, content, normalized_state)
        await self.session.commit()

        # 刷新报告以便返回最新信息
        if report_payload is None and record.report:
            report_payload = CosplayReportPayload.model_validate(record.report.result_json)

        state = self._build_state_payload(record, content, script.title, override_report=report_payload)
        return CosplaySessionStateResponse(state=state)

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

    async def _ensure_report(
        self,
        record: CosplaySession,
        content: CosplayScriptContent,
        normalized_state: dict[str, Any],
    ) -> CosplayReportPayload:
        """Ensure a report record exists for the session and return its payload."""
        if record.report is not None:
            return CosplayReportPayload.model_validate(record.report.result_json)
        report_payload = self._build_report(content, normalized_state)
        report_model = await self.repo.create_report(record.id, report_payload.model_dump(mode="json"))
        record.report = report_model
        return report_payload

    def _build_state_payload(
        self,
        record: CosplaySession,
        content: CosplayScriptContent,
        script_title: str,
        *,
        override_report: CosplayReportPayload | None = None,
    ) -> CosplaySessionState:
        """Construct a rich session state response payload from persisted data."""
        normalized_state = self._normalize_state(record.state_payload, content)
        current_scene = None
        if record.state == SessionState.in_progress:
            current_scene_index = normalized_state["current_scene_index"]
            if 0 <= current_scene_index < len(content.scenes):
                scene_def = content.scenes[current_scene_index]
                current_scene = self._build_scene_view(scene_def)
        history_models = [CosplayHistoryRecord.model_validate(entry) for entry in normalized_state["history"]]
        report_payload = override_report
        if report_payload is None and record.report is not None:
            report_payload = CosplayReportPayload.model_validate(record.report.result_json)
        return CosplaySessionState(
            session_id=record.id,
            script_id=record.script_id,
            script_title=script_title,
            setting=content.setting,
            progress=record.progress,
            completed=record.state == SessionState.completed,
            current_scene_index=normalized_state["current_scene_index"],
            total_scenes=len(content.scenes),
            scores=normalized_state["scores"],
            abilities=content.abilities,
            current_scene=current_scene,
            history=history_models,
            report=report_payload,
        )

    def _build_scene_view(self, scene: CosplaySceneDefinition) -> CosplaySceneView:
        """Return the lightweight view of a scene for front-end consumption."""
        return CosplaySceneView(
            id=scene.id,
            title=scene.title,
            narrative=scene.narrative,
            options=[
                CosplayOptionView(id=option.id, text=option.text, description=option.description)
                for option in scene.options
            ],
        )

    def _build_initial_payload(self, content: CosplayScriptContent) -> dict[str, Any]:
        """Create the default session state payload before any user choices."""
        base = content.base_score or DEFAULT_BASE_SCORE
        ability_codes = [ability.code for ability in content.abilities]
        scores = {code: base for code in ability_codes}
        return {
            "current_scene_index": 0,
            "scores": scores,
            "history": [],
        }

    def _normalize_state(
        self,
        raw_state: Any,
        content: CosplayScriptContent,
    ) -> dict[str, Any]:
        """Normalize persisted state payloads to a predictable structure."""
        state: dict[str, Any] = {}
        if isinstance(raw_state, dict):
            state.update(raw_state)
        current_scene_index = int(state.get("current_scene_index") or 0)
        current_scene_index = max(0, min(current_scene_index, len(content.scenes)))
        history = state.get("history") or []
        if not isinstance(history, list):
            history = []
        normalized_scores = self._ensure_scores_dict(state.get("scores"), content)
        return {
            "current_scene_index": current_scene_index,
            "history": list(history),
            "scores": normalized_scores,
        }

    def _ensure_scores_dict(
        self,
        raw_scores: Any,
        content: CosplayScriptContent,
    ) -> dict[str, int]:
        """Guarantee every ability code has an integer score within the state payload."""
        scores: dict[str, int] = {}
        base = content.base_score or DEFAULT_BASE_SCORE
        if isinstance(raw_scores, dict):
            for key, value in raw_scores.items():
                try:
                    scores[str(key)] = int(value)
                except (TypeError, ValueError):
                    continue
        for ability in content.abilities:
            scores.setdefault(ability.code, base)
        return scores

    def _apply_effects(
        self,
        current_scores: dict[str, int],
        option: CosplayOptionDefinition,
        *,
        abilities: Sequence[CosplayAbilityDescriptor],
        point_step: int,
        base_score: int | None,
    ) -> tuple[dict[str, int], dict[str, int]]:
        """Apply the option scoring effects and return updated totals with deltas."""
        step = point_step or DEFAULT_POINT_STEP
        baseline = base_score or DEFAULT_BASE_SCORE
        updated = {key: int(value) for key, value in current_scores.items()}
        deltas: dict[str, int] = {}
        for code, value in option.effects.items():
            try:
                delta_units = int(value)
            except (TypeError, ValueError):
                continue
            delta_points = delta_units * step
            target_code = str(code)
            # Extract fallback logic for base_value for clarity
            if target_code in updated:
                base_value = updated[target_code]
            elif target_code in current_scores:
                base_value = current_scores[target_code]
            else:
                base_value = baseline
            new_score = base_value + delta_points
            new_score = max(0, min(100, new_score))
            updated[target_code] = new_score
            if delta_points:
                deltas[target_code] = delta_points
        # 确保所有能力维度都存在
        for ability in abilities:
            updated.setdefault(ability.code, current_scores.get(ability.code, baseline))
        return updated, deltas

    def _build_history_entry(
        self,
        *,
        scene: CosplaySceneDefinition,
        option: CosplayOptionDefinition,
        delta_points: dict[str, int],
        updated_scores: dict[str, int],
    ) -> dict[str, Any]:
        """Create a historic record describing a single user choice."""
        return {
            "scene_id": scene.id,
            "scene_title": scene.title,
            "option_id": option.id,
            "option_text": option.text,
            "feedback": option.feedback,
            "delta": delta_points,
            "scores_after": updated_scores,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        }

    def _build_report(
        self,
        content: CosplayScriptContent,
        normalized_state: dict[str, Any],
    ) -> CosplayReportPayload:
        """Compile the final report summary based on accumulated scores."""
        scores = deepcopy(normalized_state["scores"])
        rules_map = self._build_rules_map(content.evaluation_rules)
        for ability in content.abilities:
            scores.setdefault(ability.code, content.base_score or DEFAULT_BASE_SCORE)
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        ranked_codes = [code for code, _ in ranked]
        max_score = ranked[0][1] if ranked else content.base_score or DEFAULT_BASE_SCORE
        min_score = ranked[-1][1] if ranked else content.base_score or DEFAULT_BASE_SCORE
        highlight_threshold = content.point_step or DEFAULT_POINT_STEP
        highlight_dimensions = [code for code, score in ranked if max_score - score <= highlight_threshold]
        if not highlight_dimensions:
            highlight_dimensions = [ranked_codes[0]] if ranked_codes else []
        if not ranked_codes or max_score - min_score < highlight_threshold:
            route_rule = rules_map.get("balanced")
            route_key = "balanced"
        else:
            first_two = tuple(sorted(ranked_codes[:2]))
            combination_key = "+".join(first_two)
            route_rule = rules_map.get(combination_key)
            route_key = combination_key
            if route_rule is None:
                route_rule = rules_map.get("balanced")
                route_key = "balanced"
        if route_rule is None:
            route_rule = CosplayEvaluationRule(
                key="balanced",
                route="团队核心路线",
                summary="你在各项能力上保持均衡发展，是团队中可靠的伙伴。",
                advice="继续保持全面发展，适时根据兴趣领域进行深化。",
            )
            route_key = "balanced"
        ability_labels = {ability.code: ability.name for ability in content.abilities}
        ability_desc = {ability.code: ability.description or "" for ability in content.abilities}
        history_models = [CosplayHistoryRecord.model_validate(item) for item in normalized_state["history"]]
        return CosplayReportPayload(
            scores=scores,
            highlight_dimensions=highlight_dimensions,
            ranked_dimensions=ranked_codes,
            route_key=route_key,
            route_name=route_rule.route,
            summary=route_rule.summary,
            advice=route_rule.advice,
            ability_labels=ability_labels,
            ability_descriptions=ability_desc,
            history=history_models,
        )

    def _build_rules_map(
        self,
        rules: Sequence[CosplayEvaluationRule],
    ) -> dict[str, CosplayEvaluationRule]:
        """Index evaluation rules by normalized key for quick lookup."""
        mapping: dict[str, CosplayEvaluationRule] = {}
        for rule in rules:
            key = rule.key.strip()
            if not key:
                continue
            if key != "balanced" and "+" in key:
                parts = [segment.strip() for segment in key.split("+") if segment.strip()]
                key = "+".join(sorted(parts))
            mapping[key] = rule
        return mapping

    def _find_option(self, scene: CosplaySceneDefinition, option_id: str) -> CosplayOptionDefinition | None:
        """Locate the option definition within the scene by its identifier."""
        for option in scene.options:
            if option.id == option_id:
                return option
        return None

    def _calculate_progress(self, current_scene_index: int, total_scenes: int) -> int:
        """Convert scene index into a rounded percentage progress value."""
        if total_scenes <= 0:
            return 0
        ratio = current_scene_index / total_scenes
        return max(0, min(100, round(ratio * 100)))

    def _parse_content(self, content: Any) -> CosplayScriptContent:
        """Validate raw JSON content into the strongly typed script model."""
        try:
            return CosplayScriptContent.model_validate(content)
        except ValidationError as exc:  # pragma: no cover - safeguards invalid data
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="剧本内容格式异常") from exc
