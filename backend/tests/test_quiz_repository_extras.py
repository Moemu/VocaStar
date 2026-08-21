from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.models.quiz import (
    Option,
    Question,
    QuestionType,
    Quiz,
    QuizAnswer,
    QuizSubmission,
    QuizSubmissionStatus,
)
from app.repositories.quiz import QuizRepository


@pytest.mark.asyncio
async def test_get_latest_published_quiz_returns_recent(database):
    repo = QuizRepository(database)

    older = Quiz(title="older-quiz", description="", is_published=True, config={})
    database.add(older)
    await database.commit()
    await database.refresh(older)
    older.created_at = older.created_at - timedelta(days=1)
    older.updated_at = older.updated_at - timedelta(days=1)
    await database.commit()

    newer = Quiz(title="newer-quiz", description="", is_published=True, config={})
    database.add(newer)
    await database.commit()
    await database.refresh(newer)
    newer.created_at = newer.created_at + timedelta(days=2)
    newer.updated_at = newer.updated_at + timedelta(days=2)
    await database.commit()

    latest = await repo.get_latest_published_quiz()
    assert latest is not None
    assert latest.id == newer.id


@pytest.mark.asyncio
async def test_get_published_quiz_by_slug(database):
    repo = QuizRepository(database)
    slug = f"slug-{uuid4().hex[:6]}"
    quiz = Quiz(title=f"quiz-{slug}", description="", is_published=True, config={"slug": slug})
    database.add(quiz)
    await database.commit()

    resolved = await repo.get_published_quiz_by_slug(slug)
    assert resolved is not None
    assert resolved.id == quiz.id

    missing = await repo.get_published_quiz_by_slug("non-existent-slug")
    assert missing is None


@pytest.mark.asyncio
async def test_clear_answers_for_questions_removes_records(database, test_user):
    repo = QuizRepository(database)

    quiz = Quiz(title="clear-answers", description="", is_published=True)
    database.add(quiz)
    await database.flush()

    question = Question(
        quiz_id=quiz.id,
        title="Q1",
        content="content",
        question_type=QuestionType.classic_scenario,
        order=1,
    )
    database.add(question)
    await database.flush()

    option = Option(question_id=question.id, content="A", dimension="R", score=1, order=1)
    database.add(option)
    await database.commit()

    submission = QuizSubmission(
        user_id=test_user.id,
        quiz_id=quiz.id,
        session_token=f"session-{uuid4().hex}",
        status=QuizSubmissionStatus.in_progress,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )
    database.add(submission)
    await database.flush()

    answer = QuizAnswer(
        submission_id=submission.id,
        question_id=question.id,
        option_id=option.id,
    )
    database.add(answer)
    await database.commit()

    await repo.clear_answers_for_questions(submission.id, [question.id])
    await database.commit()

    result = await database.execute(select(QuizAnswer).where(QuizAnswer.id == answer.id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_list_options_map_returns_cached_options(database):
    repo = QuizRepository(database)

    quiz = Quiz(title="list-options", description="", is_published=True)
    database.add(quiz)
    await database.flush()

    question_one = Question(
        quiz_id=quiz.id,
        title="Q1",
        content="content",
        question_type=QuestionType.classic_scenario,
        order=1,
    )
    question_two = Question(
        quiz_id=quiz.id,
        title="Q2",
        content="content",
        question_type=QuestionType.classic_scenario,
        order=2,
    )
    database.add_all([question_one, question_two])
    await database.flush()

    options = [
        Option(question_id=question_one.id, content="A", dimension="R", score=1, order=1),
        Option(question_id=question_one.id, content="B", dimension="I", score=1, order=2),
        Option(question_id=question_two.id, content="C", dimension="A", score=1, order=1),
    ]
    database.add_all(options)
    await database.commit()

    question_ids = [question_one.id, question_two.id]
    option_map = await repo.list_options_map(question_ids)
    assert set(option_map.keys()) == {opt.id for opt in options}

    # Re-querying should return the same mapping when passing duplicates
    option_map_duplicate = await repo.list_options_map(question_ids + [question_one.id])
    assert option_map_duplicate == option_map
