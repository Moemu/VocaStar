from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz import QuestionType, QuizAnswer, QuizSubmission
from app.schemas.quiz import QuizScoringConfig
from app.services.quiz_service import QuizService


def _make_answer(question_id: int, *, option_id=None, option_ids=None, extra_payload=None) -> QuizAnswer:
    return cast(
        QuizAnswer,
        SimpleNamespace(
            question_id=question_id,
            option_id=option_id,
            option_ids=option_ids,
            rating_value=None,
            response_time=None,
            extra_payload=extra_payload,
        ),
    )


def _build_submission(questions, config=None) -> QuizSubmission:
    quiz = SimpleNamespace(questions=questions, config=config or {})
    return cast(QuizSubmission, SimpleNamespace(quiz=quiz))


def test_count_based_scoring_respects_formula_clamping():
    service = QuizService(MagicMock(spec=AsyncSession))

    question_one = SimpleNamespace(
        id=101,
        question_type=QuestionType.classic_scenario,
        options=[
            SimpleNamespace(id=1, dimension="R", score=5, order=1),
            SimpleNamespace(id=2, dimension="I", score=4, order=2),
        ],
        settings={},
    )
    question_two = SimpleNamespace(
        id=102,
        question_type=QuestionType.classic_scenario,
        options=[SimpleNamespace(id=3, dimension="R", score=6, order=1)],
        settings={},
    )

    submission = _build_submission([question_one, question_two])
    answers = [
        _make_answer(101, option_id=1),
        _make_answer(101, option_ids=[1, 2]),
        _make_answer(102, option_id=3),
    ]

    scoring_config: QuizScoringConfig = {
        "dimension_formulas": {
            "R": {"max_occurrences": 1},
            "I": {"max_occurrences": 2},
        }
    }

    final_scores, component_scores = service._calculate_count_based_scores(answers, submission, scoring_config)

    assert final_scores["R"] == 100
    assert final_scores["I"] == 50
    assert all(dim in final_scores for dim in ["A", "S", "E", "C"])
    assert component_scores["classic_scenario"]["R"] == pytest.approx(100.0)
    assert component_scores["classic_scenario"]["I"] == pytest.approx(50.0)


def test_weighted_component_scoring_pipeline():
    service = QuizService(MagicMock(spec=AsyncSession))

    classic_question = SimpleNamespace(
        id=201,
        question_type=QuestionType.classic_scenario,
        options=[
            SimpleNamespace(id=10, dimension="R", score=5, order=1),
            SimpleNamespace(id=11, dimension="I", score=4, order=2),
        ],
        settings={},
    )
    value_question = SimpleNamespace(
        id=202,
        question_type=QuestionType.value_balance,
        options=[],
        settings={
            "scale": {"max_value": 100},
            "dimensions": [
                {"label": "动手实践", "dimension": "R"},
                {"label": "研究探索", "dimension": "I"},
            ],
        },
    )
    allocation_question = SimpleNamespace(
        id=203,
        question_type=QuestionType.time_allocation,
        options=[],
        settings={
            "max_hours": 10,
            "activities": [
                {"label": "实践任务", "dimension": "R"},
                {"label": "数据分析", "dimension": "I"},
            ],
        },
    )

    submission = _build_submission([classic_question, value_question, allocation_question])

    answers = [
        _make_answer(201, option_id=10),
        _make_answer(202, extra_payload={"values": {"动手实践": 80, "研究探索": 20}}),
        _make_answer(203, extra_payload={"allocations": {"实践任务": 6, "数据分析": 4}}),
    ]

    scoring_config: QuizScoringConfig = {
        "weights": {
            "classic_scenario": 0.5,
            "value_balance": 0.3,
            "time_allocation": 0.2,
        }
    }

    dimension_scores, component_scores = service._calculate_weighted_component_scores(
        answers, submission, scoring_config
    )

    assert dimension_scores["R"] == 86
    assert dimension_scores["I"] == 14
    assert component_scores["classic_scenario"]["R"] == pytest.approx(100.0)
    assert component_scores["value_balance"]["R"] == pytest.approx(80.0)
    assert component_scores["time_allocation"]["R"] == pytest.approx(60.0)
    assert component_scores["value_balance"]["I"] == pytest.approx(20.0)
    assert component_scores["time_allocation"]["I"] == pytest.approx(40.0)


def test_apply_weights_defaults_to_uniform_average():
    service = QuizService(MagicMock(spec=AsyncSession))
    component_scores = {
        "classic_scenario": {"R": 100.0, "I": 0.0},
        "value_balance": {"R": 50.0, "I": 50.0},
    }

    result = service._apply_weights(component_scores, {"weights": {}})
    assert result["R"] == 75
    assert result["I"] == 25


def test_deduplicate_option_ids_preserves_order():
    service = QuizService(MagicMock(spec=AsyncSession))
    assert service._deduplicate_option_ids([1, 2, 1, 3, 2, 4]) == [1, 2, 3, 4]


def test_resolve_dimension_falls_back_to_code():
    service = QuizService(MagicMock(spec=AsyncSession))
    entries = [SimpleNamespace(dimension="R", label="现实型")]
    assert service._resolve_dimension_from_validated_settings("现实型", entries) == "R"
    assert service._resolve_dimension_from_validated_settings("R", entries) == "R"
    assert service._resolve_dimension_from_validated_settings("X", entries) is None
