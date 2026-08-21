import pytest
import pytest_asyncio

from app.models.cosplay import CosplayScript


@pytest_asyncio.fixture
async def sample_cosplay_script(database, sample_careers) -> CosplayScript:
    content = {
        "summary": "测试剧本简介",
        "setting": "测试设定",
        "base_score": 50,
        "point_step": 10,
        "abilities": [
            {"code": "T", "name": "技术决策", "description": "描述 T"},
            {"code": "S", "name": "沟通协作", "description": "描述 S"},
            {"code": "P", "name": "项目管理", "description": "描述 P"},
            {"code": "Q", "name": "工匠精神", "description": "描述 Q"},
        ],
        "scenes": [
            {
                "id": "scene_1",
                "title": "场景一",
                "narrative": "描述一",
                "options": [
                    {
                        "id": "opt_a",
                        "text": "选项 A",
                        "effects": {"T": 1},
                        "feedback": "选了 A",
                    },
                    {
                        "id": "opt_b",
                        "text": "选项 B",
                        "effects": {"S": 1},
                        "feedback": "选了 B",
                    },
                ],
            },
            {
                "id": "scene_2",
                "title": "场景二",
                "narrative": "描述二",
                "options": [
                    {
                        "id": "opt_c",
                        "text": "选项 C",
                        "effects": {"Q": 1},
                        "feedback": "选了 C",
                    },
                    {
                        "id": "opt_d",
                        "text": "选项 D",
                        "effects": {"P": 1},
                        "feedback": "选了 D",
                    },
                ],
            },
        ],
        "evaluation_rules": [
            {
                "key": "T+Q",
                "route": "技术专家路线",
                "summary": "技术专家总结",
                "advice": "建议深入技术",
            },
            {
                "key": "balanced",
                "route": "团队核心路线",
                "summary": "均衡总结",
                "advice": "建议保持均衡",
            },
        ],
    }
    script = CosplayScript(career_id=sample_careers[0].id, title="测试 Cosplay 剧本", content=content)
    database.add(script)
    await database.commit()
    await database.refresh(script)
    return script


@pytest.mark.asyncio
async def test_list_cosplay_scripts(async_client, sample_cosplay_script):
    response = await async_client.get("/api/cosplay/scripts")
    assert response.status_code == 200
    payload = response.json()
    assert "scripts" in payload
    assert any(item["id"] == sample_cosplay_script.id for item in payload["scripts"])


@pytest.mark.asyncio
async def test_cosplay_flow(student_client, sample_cosplay_script):
    start_resp = await student_client.post(
        f"/api/cosplay/scripts/{sample_cosplay_script.id}/sessions", json={"resume": False}
    )
    assert start_resp.status_code == 200
    state = start_resp.json()["state"]
    assert state["current_scene"]["id"] == "scene_1"
    assert state["progress"] == 0

    choice_resp = await student_client.post(
        f"/api/cosplay/sessions/{state['session_id']}/choice",
        json={"option_id": "opt_a"},
    )
    assert choice_resp.status_code == 200
    state_after_first = choice_resp.json()["next_scene"]
    assert state_after_first["current_scene"]["id"] == "scene_2"
    assert state_after_first["scores"]["T"] == 60
    assert state_after_first["progress"] == 50

    final_resp = await student_client.post(
        f"/api/cosplay/sessions/{state['session_id']}/choice",
        json={"option_id": "opt_c"},
    )
    assert final_resp.status_code == 200
    final_state = final_resp.json()["next_scene"]
    assert final_state["completed"] is True
    assert final_state["progress"] == 100
    assert final_state["current_scene"] is None
    assert len(final_state["history"]) == 2

    report_resp = await student_client.get(f"/api/cosplay/sessions/{state['session_id']}/report")
    assert report_resp.status_code == 200
    report_payload = report_resp.json()
    assert report_payload["final_scores"]["T"] == 60
    assert report_payload["final_scores"]["Q"] == 60
