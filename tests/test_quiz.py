from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career import CareerRecommendation
from app.models.extensions import UserPoints
from app.models.quiz import Quiz
from app.models.user import User


async def test_quiz_flow(
    student_client: AsyncClient,
    sample_quiz: Quiz,
    test_user: User,
    database: AsyncSession,
):
    start_response = await student_client.post("/api/quiz/start", params={"slug": "test-classic"})
    assert start_response.status_code == 200
    start_payload = start_response.json()
    session_id = start_payload["session_id"]
    assert "server_time" in start_payload
    assert "expires_at" in start_payload

    questions_response = await student_client.get("/api/quiz/questions", params={"session_id": session_id})
    assert questions_response.status_code == 200
    questions_payload = questions_response.json()
    assert "server_time" in questions_payload
    questions = questions_payload["questions"]
    assert len(questions) > 0
    assert all(question.get("selected_option_id") is None for question in questions)

    answers = [
        {
            "question_id": question["question_id"],
            "type": "single_choice",
            "option_id": question["options"][0]["id"],
            "response_time": 5,
        }
        for question in questions
    ]

    answer_response = await student_client.post(
        "/api/quiz/answer",
        json={"session_id": session_id, "answers": answers},
    )
    assert answer_response.status_code == 200
    questions_after_answer = await student_client.get("/api/quiz/questions", params={"session_id": session_id})
    assert questions_after_answer.status_code == 200
    answered_questions = questions_after_answer.json()["questions"]
    assert all(question.get("selected_option_id") is not None for question in answered_questions)

    submit_response = await student_client.post(
        "/api/quiz/submit",
        json={"session_id": session_id},
    )
    assert submit_response.status_code == 200
    submit_payload = submit_response.json()
    report = submit_payload["report"]
    assert report["holland_code"]
    assert report["reward_points"] == 80
    assert report["dimension_scores"]
    assert report["recommendations"]
    assert all(0 <= item["match_score"] <= 100 for item in report["recommendations"])

    recommendation_result = await database.execute(select(CareerRecommendation))
    recommendation_records = recommendation_result.scalars().all()
    assert recommendation_records, "职业推荐应当持久化到 career_recommendations 表"
    recommendation_ids = {record.career_id for record in recommendation_records}
    response_ids = {item["profession_id"] for item in report["recommendations"]}
    assert response_ids.issubset(recommendation_ids)
    assert len(recommendation_records) >= len(response_ids)

    submit_second = await student_client.post(
        "/api/quiz/submit",
        json={"session_id": session_id},
    )
    assert submit_second.status_code == 200
    assert submit_second.json()["report"] == report

    report_by_slug = await student_client.get("/api/quiz/report", params={"slug": "test-classic"})
    assert report_by_slug.status_code == 200
    fetched_report = report_by_slug.json()["report"]
    assert fetched_report == report

    latest_report_response = await student_client.get("/api/quiz/report")
    assert latest_report_response.status_code == 200
    assert latest_report_response.json()["report"] == report

    result = await database.execute(select(UserPoints).where(UserPoints.user_id == test_user.id))
    user_points = result.scalars().first()
    assert user_points is not None
    assert user_points.points >= report["reward_points"]


async def test_start_quiz_with_invalid_slug(
    student_client: AsyncClient,
):
    response = await student_client.post("/api/quiz/start", params={"slug": "non-existent"})
    assert response.status_code == 404
