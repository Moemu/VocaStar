from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.models.quiz import QuizReport, QuizSubmission, QuizSubmissionStatus


@pytest.mark.asyncio
async def test_list_careers(student_client, sample_careers):
    response = await student_client.get("/api/career/", params={"limit": 2, "offset": 0})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= len(sample_careers)
    assert len(payload["items"]) == 2
    first = payload["items"][0]
    assert first.get("competency_requirements")
    assert first["competency_requirements"]["core_competency_model"]
    assert first["name"]
    assert isinstance(first.get("related_courses"), list)
    assert first["skills_snapshot"]


@pytest.mark.asyncio
async def test_filter_by_dimension(student_client):
    response = await student_client.get("/api/career/", params={"dimension": "R"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["items"], "应返回至少一个匹配 R 维度的职业"
    for item in payload["items"]:
        assert "R" in item.get("holland_dimensions", [])


@pytest.mark.asyncio
async def test_get_career_detail(student_client, sample_careers):
    target = sample_careers[0]
    response = await student_client.get(f"/api/career/{target.id}")
    assert response.status_code == 200
    detail = response.json()
    assert detail["name"] == target.name
    assert detail["skill_map"]["skills_snapshot"]
    assert detail["competency_requirements"]["core_competency_model"]["basic_ability"] == pytest.approx(4)
    assert detail["related_courses"] and isinstance(detail["related_courses"], list)
    assert detail["competency_requirements"]["knowledge_background"]["industry_knowledge"]
    assert detail["galaxy_name"]
    assert detail["salary_min"] is not None
    assert detail["skills_snapshot"]


@pytest.mark.asyncio
async def test_featured_careers(student_client):
    response = await student_client.get("/api/career/featured", params={"limit": 3})
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 3
    assert all("name" in item for item in items)
    assert all(isinstance(item.get("related_courses"), list) for item in items)


@pytest.mark.asyncio
async def test_career_exploration_basic(student_client, sample_careers):
    response = await student_client.get("/api/career/exploration")
    assert response.status_code == 200
    payload = response.json()
    assert payload["galaxies"], "应返回带有职业的星系列表"
    first_galaxy = payload["galaxies"][0]
    assert "id" in first_galaxy and first_galaxy["planets"], "星系需要包含职业星球数据"
    planet = first_galaxy["planets"][0]
    assert planet["skills_snapshot"]
    assert payload["filters"]["categories"], "应返回可用的分类筛选"


@pytest.mark.asyncio
async def test_career_exploration_filter_by_category(student_client, sample_careers):
    response = await student_client.get(
        "/api/career/exploration",
        params={"category": "互联网·通信"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["galaxies"], "过滤后仍应返回星系"
    for galaxy in payload["galaxies"]:
        assert galaxy["category"] == "互联网·通信"


@pytest.mark.asyncio
async def test_career_exploration_salary_filter(student_client, sample_careers):
    response = await student_client.get(
        "/api/career/exploration",
        params={"salary_min": "10000", "salary_max": "16000"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["galaxies"]
    for galaxy in payload["galaxies"]:
        for planet in galaxy["planets"]:
            if planet["salary_min"] is not None:
                assert planet["salary_min"] <= 16000
            if planet["salary_max"] is not None:
                assert planet["salary_max"] >= 10000


@pytest.mark.asyncio
async def test_career_exploration_recommended(student_client, database, test_user, sample_quiz, sample_careers):
    now = datetime.now(timezone.utc)
    submission = QuizSubmission(
        user_id=test_user.id,
        quiz_id=sample_quiz.id,
        session_token=f"test-token-{uuid4()}",
        status=QuizSubmissionStatus.completed,
        expires_at=now + timedelta(days=1),
        completed_at=now,
    )
    database.add(submission)
    await database.flush()

    report_payload = {
        "holland_code": "RI",
        "dimension_scores": {"R": 30, "I": 25},
        "recommendations": [],
        "reward_points": 0,
    }
    report = QuizReport(submission_id=submission.id, result_json=report_payload)
    database.add(report)
    await database.commit()

    response = await student_client.get(
        "/api/career/exploration",
        params={"recommended": "true"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["galaxies"], "启用推荐后应返回匹配职业"
    for galaxy in payload["galaxies"]:
        for planet in galaxy["planets"]:
            dimensions = planet.get("holland_dimensions") or []
            assert any(letter in {"R", "I"} for letter in dimensions), "返回的职业应匹配霍兰德维度"
