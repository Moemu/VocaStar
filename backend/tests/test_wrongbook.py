import pytest
import pytest_asyncio

from app.models.cosplay import CosplayScript


@pytest_asyncio.fixture
async def script_with_answer(database, sample_careers) -> CosplayScript:
    content = {
        "summary": "剧本含正确答案",
        "setting": "设定",
        "base_score": 50,
        "point_step": 10,
        "abilities": [
            {"code": "T", "name": "技术决策"},
            {"code": "S", "name": "沟通协作"},
        ],
        "scenes": [
            {
                "id": "s1",
                "title": "第一幕",
                "narrative": "请选择",
                "options": [
                    {"id": "A", "text": "A 选项", "effects": {"T": 1}, "feedback": "A"},
                    {"id": "B", "text": "B 选项", "effects": {"S": 1}, "feedback": "B"},
                ],
                "correct_option_id": "B",
                "explanation": "因为 B 更符合需求沟通与推进。",
            },
        ],
        "evaluations": [],
    }
    script = CosplayScript(career_id=sample_careers[0].id, title="含正确答案剧本", content=content)
    database.add(script)
    await database.commit()
    await database.refresh(script)
    return script


@pytest.mark.asyncio
async def test_wrongbook_flow(student_client, script_with_answer):
    # 开始会话
    resp = await student_client.post(f"/api/cosplay/scripts/{script_with_answer.id}/sessions", json={"resume": False})
    assert resp.status_code == 200
    state = resp.json()["state"]
    # 选择错误答案（A）
    resp2 = await student_client.post(f"/api/cosplay/sessions/{state['session_id']}/choice", json={"option_id": "A"})
    assert resp2.status_code == 200

    # 查询错题本
    wb = await student_client.get("/api/profile/wrongbook")
    assert wb.status_code == 200
    payload = wb.json()
    assert "items" in payload
    assert len(payload["items"]) >= 1
    item = payload["items"][0]
    assert item["script_title"] == "含正确答案剧本"
    assert item["scene_title"] == "第一幕"
    assert item["selected_option_text"] == "A 选项"
    assert item["correct_option_text"] == "B 选项"
    assert "因为" in item["analysis"]
