"""Utility script to import quiz definitions from a YAML file into the database.

Usage examples
--------------
Run with default configuration (assets/quizs.yaml) and only create quizzes that do not yet exist::

    uv run python scripts/import_quiz_from_yaml.py

Force re-import even if a quiz with the same title already exists (only allowed when
no submissions were recorded for that quiz)::

    uv run python scripts/import_quiz_from_yaml.py --force

Select a different YAML file::

    uv run python scripts/import_quiz_from_yaml.py --yaml-path path/to/file.yaml
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.core.logger import logger  # noqa:E402
from app.core.sql import async_session_maker  # noqa:E402
from app.models.quiz import Option, Question, QuestionType, Quiz  # noqa:E402

# Keys that belong to the question model directly, everything else falls back into settings.
QUESTION_BASE_FIELDS = {"title", "content", "question_type", "order", "is_required", "options"}


async def ensure_image_option_support(session: AsyncSession) -> None:
    """确保 options 表拥有 image_url 列，兼容旧版数据库。"""

    result = await session.execute(text("PRAGMA table_info(options)"))
    columns = {row[1] for row in result.fetchall()}  # type: ignore[index]
    if "image_url" not in columns:
        logger.warning("检测到旧版数据库缺少列 options.image_url，正在自动新增")
        await session.execute(text("ALTER TABLE options ADD COLUMN image_url VARCHAR(500)"))


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"YAML 文件不存在: {path}")
    with path.open("r", encoding="utf-8") as fp:
        data = yaml.safe_load(fp)
    if not isinstance(data, dict):
        raise ValueError("题库配置文件的根节点必须是一个字典对象")
    return data


async def import_quiz(
    session: AsyncSession,
    *,
    slug: str,
    payload: Dict[str, Any],
    force: bool,
) -> Tuple[Quiz, bool]:
    """Create or update a quiz based on the payload.

    Returns the quiz instance and a flag that indicates whether it was newly created.
    """

    title = payload.get("title")
    if not title:
        raise ValueError(f"题库节点 {slug!r} 缺少 title 字段")

    description = payload.get("description")
    is_published = bool(payload.get("is_published", False))

    quiz_stmt = select(Quiz).where(Quiz.title == title)
    quiz_result = await session.execute(quiz_stmt)
    quiz = quiz_result.scalars().unique().first()

    extra_config = {
        key: value for key, value in payload.items() if key not in {"title", "description", "is_published", "questions"}
    }
    extra_config["slug"] = slug

    created = False
    if quiz:
        await session.refresh(quiz, attribute_names=["submissions"])
        if quiz.submissions:
            if force:
                raise RuntimeError(f"测评 {title!r} 已存在提交记录，出于安全考虑不允许强制覆盖。")
            logger.warning("跳过题库 %s：已存在并且检测到提交记录", title)
            return quiz, False

        if not force:
            logger.info("跳过题库 %s：已存在，可使用 --force 覆盖", title)
            return quiz, False

        # 删除旧问题（及级联选项），重新导入
        await session.refresh(quiz, attribute_names=["questions"])
        if quiz.questions:
            question_ids = [question.id for question in quiz.questions]
            await session.execute(delete(Option).where(Option.question_id.in_(question_ids)))
            await session.execute(delete(Question).where(Question.id.in_(question_ids)))
    else:
        quiz = Quiz(title=title, description=description, is_published=is_published, config=extra_config)
        session.add(quiz)
        await session.flush()
        created = True

    if not created:
        quiz.description = description
        quiz.is_published = is_published
        quiz.config = extra_config  # type:ignore
        await session.flush()

    # 重新装载 quiz，确保可用 ID
    await session.refresh(quiz)

    questions = payload.get("questions", [])
    if not isinstance(questions, list):
        raise ValueError(f"题库 {title!r} 的 questions 字段必须是列表")

    for idx, question_payload in enumerate(questions, start=1):
        if not isinstance(question_payload, dict):
            raise ValueError(f"题库 {title!r} 的第 {idx} 个题目不是有效的对象")

        q_type_raw = question_payload.get("question_type")
        try:
            question_type = QuestionType(q_type_raw)
        except ValueError as exc:
            raise ValueError(
                f"题库 {title!r} 的第 {idx} 个题目 question_type 字段值无效: {q_type_raw}，请检查枚举类型。"
            ) from exc

        question = Question(
            quiz_id=quiz.id,
            title=question_payload.get("title"),
            content=question_payload.get("content") or "",
            question_type=question_type,
            order=int(question_payload.get("order", idx)),
            is_required=bool(question_payload.get("is_required", True)),
            settings={key: value for key, value in question_payload.items() if key not in QUESTION_BASE_FIELDS},
        )

        options_payload = question_payload.get("options") or []
        if not isinstance(options_payload, list):
            raise ValueError(f"题库 {title!r} 的第 {idx} 个题目 options 字段必须是列表")

        for opt_idx, option_payload in enumerate(options_payload, start=1):
            if not isinstance(option_payload, dict):
                raise ValueError(f"题库 {title!r} 的第 {idx} 个题目包含无效选项（位置 {opt_idx} ）")
            option = Option(
                content=option_payload.get("content") or "",
                image_url=option_payload.get("image_url"),
                dimension=option_payload.get("dimension"),
                score=int(option_payload.get("score", 0)),
                order=int(option_payload.get("order", opt_idx)),
            )
            question.options.append(option)

        session.add(question)

    logger.info("题库 %s 导入完成，共导入 %d 道题目", title, len(questions))
    return quiz, created


async def async_main(args: argparse.Namespace) -> None:
    yaml_path = Path(args.yaml_path)
    payload = load_yaml(yaml_path)

    async with async_session_maker() as session:
        await ensure_image_option_support(session)
        for slug, quiz_payload in payload.items():
            if not isinstance(quiz_payload, dict):
                raise ValueError(f"题库节点 {slug!r} 必须是对象")
            await import_quiz(session, slug=slug, payload=quiz_payload, force=args.force)
        await session.commit()

    logger.info("所有题库导入完成 ✅")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="导入 YAML 题库配置到数据库")
    parser.add_argument(
        "--yaml-path",
        type=str,
        default=str(Path("assets") / "quizzes.yaml"),
        help="题库配置文件路径 (默认为 assets/quizzes.yaml)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="若题库已存在，则强制覆盖（当且仅当不存在提交记录时可用）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":  # pragma: no cover
    main()
