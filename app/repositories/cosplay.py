from __future__ import annotations

from typing import Any, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cosplay import (
    CosplayReport,
    CosplayScript,
    CosplaySession,
    SessionState,
)
from app.models.extensions import CosplayWrongbook
from app.schemas.cosplay import CosplayReportPayload


class CosplayRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_scripts(self) -> Sequence[CosplayScript]:
        stmt = select(CosplayScript).order_by(CosplayScript.id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_script_by_id(self, script_id: int) -> Optional[CosplayScript]:
        stmt = select(CosplayScript).where(CosplayScript.id == script_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_active_session(self, user_id: int, script_id: int) -> Optional[CosplaySession]:
        stmt = (
            select(CosplaySession)
            .options(selectinload(CosplaySession.report))
            .where(
                CosplaySession.user_id == user_id,
                CosplaySession.script_id == script_id,
                CosplaySession.state == SessionState.in_progress,
            )
            .order_by(CosplaySession.started_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_session_by_id(self, session_id: int) -> Optional[CosplaySession]:
        stmt = (
            select(CosplaySession).options(selectinload(CosplaySession.report)).where(CosplaySession.id == session_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_session(
        self,
        *,
        user_id: int,
        script_id: int,
        state_payload: dict[str, Any],
    ) -> CosplaySession:
        session = CosplaySession(
            user_id=user_id,
            script_id=script_id,
            progress=0,
            state=SessionState.in_progress,
            state_payload=state_payload,
        )
        self.session.add(session)
        await self.session.flush()
        await self.session.refresh(session)
        return session

    async def create_report(self, session_id: int, payload: CosplayReportPayload) -> CosplayReport:
        report = CosplayReport(session_id=session_id, result_json=payload.model_dump(mode="json"))
        self.session.add(report)
        await self.session.flush()
        await self.session.refresh(report)
        return report

    async def upsert_wrongbook(
        self,
        *,
        user_id: int,
        script_id: int,
        scene_id: str,
        script_title: str,
        scene_title: str,
        selected_option_text: str,
        correct_option_text: str,
        analysis: str | None,
    ) -> CosplayWrongbook:
        """插入或更新一条错题本记录（同一 user/script/scene 唯一）。"""
        stmt = select(CosplayWrongbook).where(
            CosplayWrongbook.user_id == user_id,
            CosplayWrongbook.script_id == script_id,
            CosplayWrongbook.scene_id == scene_id,
        )
        result = await self.session.execute(stmt)
        row = result.scalars().first()
        if row:
            row.script_title = script_title
            row.scene_title = scene_title
            row.selected_option_text = selected_option_text
            row.correct_option_text = correct_option_text
            row.analysis = analysis
            return row
        row = CosplayWrongbook(
            user_id=user_id,
            script_id=script_id,
            scene_id=scene_id,
            script_title=script_title,
            scene_title=scene_title,
            selected_option_text=selected_option_text,
            correct_option_text=correct_option_text,
            analysis=analysis,
        )
        self.session.add(row)
        await self.session.flush()
        await self.session.refresh(row)
        return row
