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

    async def create_report(self, session_id: int, payload: dict[str, Any]) -> CosplayReport:
        report = CosplayReport(session_id=session_id, result_json=payload)
        self.session.add(report)
        await self.session.flush()
        await self.session.refresh(report)
        return report
