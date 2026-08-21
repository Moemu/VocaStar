from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 让脚本可从项目根目录导入 `app`
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.sql import Base  # noqa: E402
from app.models.extensions import Achievement  # noqa: E402
from app.services.achievement_service import AchievementService  # noqa: E402

RAW_DB_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL") or "sqlite+aiosqlite:///app/data/app.db"

# 兼容用户将 DB_URL 设为 sqlite:/// 的情况
DB_URL = RAW_DB_URL
if DB_URL.startswith("sqlite:///") and not DB_URL.startswith("sqlite+aiosqlite:///"):
    DB_URL = DB_URL.replace("sqlite:///", "sqlite+aiosqlite:///", 1)


async def main() -> None:
    # 确保目录存在
    if DB_URL.startswith("sqlite+aiosqlite:///"):
        db_file = DB_URL.replace("sqlite+aiosqlite:///", "", 1)
        db_dir = os.path.dirname(db_file)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    engine = create_async_engine(DB_URL, future=True)

    # 若基础表尚未创建，则创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        svc = AchievementService(session)
        await svc.seed_minimal()
        # 输出结果
        rows = (await session.execute(select(Achievement))).scalars().all()
        for a in rows:
            print(f"[seed] {a.code} - {a.name} (threshold={a.threshold})")


if __name__ == "__main__":
    asyncio.run(main())
    print("[seed] achievements minimal seed done.")
