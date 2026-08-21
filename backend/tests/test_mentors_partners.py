import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mentors import CommunityMentor, CommunityMentorSkill
from app.models.partners import (
    CommunityPartner,
    CommunityPartnerSkill,
)


@pytest.mark.asyncio
async def test_list_domains_and_search_mentors(database: AsyncSession, async_client: AsyncClient):
    # seed mentors
    m1 = CommunityMentor(name="Alice", profession="前端开发")
    m2 = CommunityMentor(name="Bob", profession="数据分析")
    database.add_all([m1, m2])
    await database.flush()
    # attach skills
    database.add_all(
        [
            CommunityMentorSkill(mentor_id=m1.id, skill="react"),
            CommunityMentorSkill(mentor_id=m1.id, skill="typescript"),
            CommunityMentorSkill(mentor_id=m2.id, skill="sql"),
        ]
    )
    await database.commit()

    # domains auto ensure (ensure_domains invoked inside list_domains_with_counts)
    resp_domains = await async_client.get("/api/community/mentors/domains")
    assert resp_domains.status_code == 200
    domains = resp_domains.json()["items"]
    assert any(d["slug"] == "frontend" for d in domains)

    # search mentors by q
    resp_q = await async_client.get("/api/community/mentors/search?q=前端")
    assert resp_q.status_code == 200
    items_q = resp_q.json()["items"]
    assert any("前端" in it["profession"] for it in items_q)

    # search by skill filter
    resp_skill = await async_client.get("/api/community/mentors/search?skill=react")
    assert resp_skill.status_code == 200
    items_skill = resp_skill.json()["items"]
    assert all("react" in it["tech_stack"] for it in items_skill)


@pytest.mark.asyncio
async def test_partner_search_bind_unbind_and_recommend(database: AsyncSession, student_client: AsyncClient):
    # seed partners
    p1 = CommunityPartner(name="Carol", profession="后端开发", learning_progress=40)
    p2 = CommunityPartner(name="Dave", profession="数据分析", learning_progress=60)
    database.add_all([p1, p2])
    await database.flush()
    database.add_all(
        [
            CommunityPartnerSkill(partner_id=p1.id, skill="python"),
            CommunityPartnerSkill(partner_id=p1.id, skill="fastapi"),
            CommunityPartnerSkill(partner_id=p2.id, skill="sql"),
        ]
    )
    await database.commit()

    # search partners by skill
    resp_search = await student_client.get("/api/community/partners/search?skill=python")
    assert resp_search.status_code == 200
    items = resp_search.json()["items"]
    assert any("python" in it["tech_stack"] for it in items)

    # bind partner p1
    bind_resp = await student_client.post(f"/api/community/partners/{p1.id}/bind")
    assert bind_resp.status_code == 200
    assert bind_resp.json()["bound"] is True
    # bind again idempotent
    bind_again = await student_client.post(f"/api/community/partners/{p1.id}/bind")
    assert bind_again.status_code == 200
    assert bind_again.json()["bound"] is True

    # my partners should list p1
    mine_resp = await student_client.get("/api/community/partners/my")
    assert mine_resp.status_code == 200
    my_items = mine_resp.json()["items"]
    assert any(it["name"] == "Carol" for it in my_items)

    # recommend should exclude already bound p1 if user logged in
    rec_resp = await student_client.get("/api/community/partners/recommended")
    assert rec_resp.status_code == 200
    rec_items = rec_resp.json()["items"]
    assert all(it["name"] != "Carol" for it in rec_items) or rec_items == []

    # unbind partner
    unbind_resp = await student_client.delete(f"/api/community/partners/{p1.id}/bind")
    assert unbind_resp.status_code == 200
    assert unbind_resp.json()["bound"] is False

    # recommended can include Carol again now
    rec_after_unbind = await student_client.get("/api/community/partners/recommended")
    assert rec_after_unbind.status_code == 200
    after_items = rec_after_unbind.json()["items"]
    # Accept both presence/absence depending on recommendation logic but ensure response structure
    for it in after_items:
        assert "id" in it and "tech_stack" in it
