from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career import CareerRecommendation
from app.models.extensions import UserPoints
from app.models.quiz import Quiz, UserProfile
from app.models.user import User


async def test_quiz_flow(
    student_client: AsyncClient,
    sample_quiz: Quiz,
    test_user: User,
    database: AsyncSession,
):
    # Test profile submission (before starting quiz)
    profile_response = await student_client.post(
        "/api/quiz/profile",
        json={
            "career_stage": "大学生",
            "major": "计算机科学",
            "career_confusion": "不确定未来从事什么方向",
            "short_term_goals": ["找到合适的专业方向", "获得实习机会"],
        },
    )
    assert profile_response.status_code == 200
    profile_data = profile_response.json()
    assert profile_data["career_stage"] == "大学生"
    assert profile_data["major"] == "计算机科学"
    assert len(profile_data["short_term_goals"]) == 2

    # Verify profile was saved to user (not session)
    result = await database.execute(select(UserProfile).where(UserProfile.user_id == test_user.id))
    profile = result.scalars().first()
    assert profile is not None
    assert profile.career_stage == "大学生"
    assert profile.major == "计算机科学"
    assert profile.career_confusion == "不确定未来从事什么方向"
    assert len(profile.short_term_goals) == 2

    # Start quiz after profile
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
            "type": "classic_scenario",
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


async def test_profile_validation(
    student_client: AsyncClient,
    sample_quiz: Quiz,
):
    """
    Test the validation logic for the quiz profile submission,
    including invalid career stage, empty goals, normal submission, update, and GET profile.
    """

    # Test invalid career stage
    invalid_stage_response = await student_client.post(
        "/api/quiz/profile",
        json={
            "career_stage": "无效阶段",
            "major": "计算机科学",
            "career_confusion": "测试困惑",
            "short_term_goals": ["目标1"],
        },
    )
    assert invalid_stage_response.status_code == 422

    # Test empty short term goals
    empty_goals_response = await student_client.post(
        "/api/quiz/profile",
        json={
            "career_stage": "大学生",
            "major": "计算机科学",
            "career_confusion": "测试困惑",
            "short_term_goals": [],
        },
    )
    assert empty_goals_response.status_code == 422

    # Test normal submission
    valid_response = await student_client.post(
        "/api/quiz/profile",
        json={
            "career_stage": "大学生",
            "major": "计算机科学",
            "career_confusion": "测试困惑",
            "short_term_goals": ["目标1"],
        },
    )
    assert valid_response.status_code == 200
    profile_data = valid_response.json()
    assert profile_data["career_stage"] == "大学生"

    # Test update (not duplicate - should update existing)
    update_response = await student_client.post(
        "/api/quiz/profile",
        json={
            "career_stage": "职场新人",
            "major": "金融",
            "career_confusion": "另一个困惑",
            "short_term_goals": ["目标2"],
        },
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["career_stage"] == "职场新人"
    assert updated_data["major"] == "金融"

    # Test GET profile
    get_response = await student_client.get("/api/quiz/profile")
    assert get_response.status_code == 200
    fetched_data = get_response.json()
    assert fetched_data["career_stage"] == "职场新人"
    assert fetched_data["major"] == "金融"


async def test_start_quiz_with_invalid_slug(
    student_client: AsyncClient,
):
    response = await student_client.post("/api/quiz/start", params={"slug": "non-existent"})
    assert response.status_code == 404
