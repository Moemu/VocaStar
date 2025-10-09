import pytest


@pytest.mark.asyncio
async def test_list_careers(student_client, sample_careers):
    response = await student_client.get("/api/career/", params={"limit": 2, "offset": 0})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= len(sample_careers)
    assert len(payload["items"]) == 2
    first = payload["items"][0]
    assert "core_competency_model" in first
    assert first["name"]


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
    assert detail["required_skills"] and isinstance(detail["required_skills"], list)
    assert detail["core_competency_model"]["basic_ability"] == pytest.approx(4)


@pytest.mark.asyncio
async def test_featured_careers(student_client):
    response = await student_client.get("/api/career/featured", params={"limit": 3})
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 3
    assert all("name" in item for item in items)
