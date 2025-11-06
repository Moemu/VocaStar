import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.community import (
    CommunityCategory,
    CommunityGroup,
    CommunityGroupMember,
    CommunityPost,
    CommunityPostAttachment,
)
from app.models.user import User


@pytest.mark.asyncio
async def test_list_categories_and_group_counts(database: AsyncSession, async_client: AsyncClient):
    # prepare categories and groups
    cat1 = CommunityCategory(slug="frontend", name="前端", order=1)
    cat2 = CommunityCategory(slug="design", name="设计", order=2)
    database.add_all([cat1, cat2])
    await database.flush()
    g1 = CommunityGroup(title="前端学习组", summary="一起学习前端", category_id=cat1.id)
    g2 = CommunityGroup(title="设计组", summary="一起讨论设计", category_id=cat2.id)
    g3 = CommunityGroup(title="再一个前端组", summary="更多前端", category_id=cat1.id)
    database.add_all([g1, g2, g3])
    await database.commit()

    resp = await async_client.get("/api/community/groups/categories")
    assert resp.status_code == 200
    data = resp.json()
    # counts should reflect groups per category
    items = {item["slug"]: item for item in data["items"]}
    assert items["frontend"]["count"] == 2
    assert items["design"]["count"] == 1


@pytest.mark.asyncio
async def test_join_leave_group_idempotent(database: AsyncSession, student_client: AsyncClient):
    cat = CommunityCategory(slug="product", name="产品", order=1)
    database.add(cat)
    await database.flush()
    group = CommunityGroup(title="产品组", summary="讨论产品", category_id=cat.id)
    database.add(group)
    await database.commit()

    # join
    join_resp = await student_client.post(f"/api/community/groups/{group.id}/join")
    assert join_resp.status_code == 200
    first = join_resp.json()
    assert first["joined"] is True
    members_count = first["members_count"]

    # join again - idempotent
    join_again = await student_client.post(f"/api/community/groups/{group.id}/join")
    assert join_again.status_code == 200
    assert join_again.json()["members_count"] == members_count
    assert join_again.json()["joined"] is True

    # leave
    leave_resp = await student_client.delete(f"/api/community/groups/{group.id}/membership")
    assert leave_resp.status_code == 200
    leave_data = leave_resp.json()
    assert leave_data["joined"] is False

    # leave again - idempotent
    leave_again = await student_client.delete(f"/api/community/groups/{group.id}/membership")
    assert leave_again.status_code == 200
    assert leave_again.json()["joined"] is False


@pytest.mark.asyncio
async def test_group_detail_owner_and_rules_fallback(
    database: AsyncSession, async_client: AsyncClient, student_client: AsyncClient, test_user: User
):
    cat = CommunityCategory(slug="backend", name="后端", order=1)
    database.add(cat)
    await database.flush()
    # group with explicit owner and rules
    g1 = CommunityGroup(
        title="后端组",
        summary="一起学后端",
        category_id=cat.id,
        owner_name="OwnerA",
        owner_avatar_url="/static/avatars/a.png",
        rules_json='["文明交流","禁止广告"]',
    )
    # group without owner -> fallback to leader membership
    g2 = CommunityGroup(
        title="无主组",
        summary="需要fallback",
        category_id=cat.id,
        rules_json=None,  # None triggers fallback to empty list
    )
    database.add_all([g1, g2])
    await database.flush()
    # leader membership for g2
    leader = CommunityGroupMember(group_id=g2.id, user_id=test_user.id, role="leader")
    database.add(leader)
    await database.commit()

    # unauth detail for g1
    r1 = await async_client.get(f"/api/community/groups/{g1.id}")
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["meta"]["owner"]["name"] == "OwnerA"
    assert d1["rules"] == ["文明交流", "禁止广告"]
    assert d1["joined"] is False

    # auth detail for g2 (should fallback owner, rules empty)
    r2 = await student_client.get(f"/api/community/groups/{g2.id}")
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["rules"] == []  # invalid JSON fallback
    assert d2["meta"]["owner"]["name"] != ""  # fallback leader name (may be username)

    # not found
    nf = await async_client.get("/api/community/groups/999999")
    assert nf.status_code == 404


@pytest.mark.asyncio
async def test_my_groups_and_list_groups_joined_flag(
    database: AsyncSession, async_client: AsyncClient, student_client: AsyncClient
):
    cat = CommunityCategory(slug="data", name="数据", order=1)
    database.add(cat)
    await database.flush()
    g = CommunityGroup(title="数据分析组", summary="学习数据分析", category_id=cat.id)
    database.add(g)
    await database.commit()
    # join with auth client
    await student_client.post(f"/api/community/groups/{g.id}/join")

    # list my groups (auth)
    my_resp = await student_client.get("/api/community/groups/my")
    assert my_resp.status_code == 200
    items = my_resp.json()["items"]
    assert any(item["joined"] is True for item in items)

    # unauth list_groups - joined should be False
    # remove auth header to simulate unauthenticated request (student_client/async_client share instance)
    async_client.headers.pop("Authorization", None)
    list_resp = await async_client.get("/api/community/groups")
    assert list_resp.status_code == 200
    for item in list_resp.json()["items"]:
        assert item["joined"] is False


@pytest.mark.asyncio
async def test_group_members_ordering(database: AsyncSession, async_client: AsyncClient):
    cat = CommunityCategory(slug="ml", name="机器学习", order=1)
    database.add(cat)
    await database.flush()
    grp = CommunityGroup(title="ML组", summary="讨论ML", category_id=cat.id)
    database.add(grp)
    await database.flush()
    # create minimal users to satisfy join query
    u1 = User(username="leader_user", password_hash="x", email="l@example.com")
    u2 = User(username="mem_user1", password_hash="x", email="m1@example.com")
    u3 = User(username="mem_user2", password_hash="x", email="m2@example.com")
    database.add_all([u1, u2, u3])
    await database.flush()
    # create members: leader first, then others
    m_leader = CommunityGroupMember(group_id=grp.id, user_id=u1.id, role="leader")
    m2 = CommunityGroupMember(group_id=grp.id, user_id=u2.id, role="member")
    m3 = CommunityGroupMember(group_id=grp.id, user_id=u3.id, role="member")
    database.add_all([m_leader, m2, m3])
    await database.commit()

    resp = await async_client.get(f"/api/community/groups/{grp.id}/members")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert items[0]["role"] == "leader"
    assert {items[1]["role"], items[2]["role"]} == {"member"}


@pytest.mark.asyncio
async def test_publish_post_like_and_repository_list(database: AsyncSession, student_client: AsyncClient):
    cat = CommunityCategory(slug="devops", name="DevOps", order=1)
    database.add(cat)
    await database.flush()
    grp = CommunityGroup(title="DevOps组", summary="CI/CD讨论", category_id=cat.id)
    database.add(grp)
    await database.commit()

    # publish a post with attachments (simulate URL + document + image + code)
    payload = {
        "group_id": grp.id,
        "title": "第一次发布",
        "content": "这是内容",
        "attachments": [
            {"type": "document", "url": "http://example.com/doc1", "title": "文档1", "file_size": 123},
            {"type": "image", "url": "http://example.com/img.png"},
            {"type": "code", "url": "http://example.com/code.py", "title": "代码片段", "file_size": 77},
        ],
    }
    pub = await student_client.post("/api/community/groups/posts", json=payload)
    assert pub.status_code == 200
    post_id = pub.json()["id"]

    # like/unlike post
    like_post = await student_client.post(f"/api/community/groups/posts/{post_id}/like")
    assert like_post.status_code == 200
    assert like_post.json()["liked"] is True
    like_post_again = await student_client.post(f"/api/community/groups/posts/{post_id}/like")
    assert like_post_again.json()["liked"] is True  # idempotent

    # comment
    comment_resp = await student_client.post(
        f"/api/community/groups/posts/{post_id}/comments", json={"content": "不错的帖子"}
    )
    assert comment_resp.status_code == 200
    assert comment_resp.json()["content"] == "不错的帖子"

    # repository list - should include only document/code types
    repo_resp = await student_client.get("/api/community/groups/repository")
    assert repo_resp.status_code == 200
    repo_items = repo_resp.json()["items"]
    types = {i["type"] for i in repo_items}
    assert "document" in types and "code" in types
    assert "image" not in types  # image excluded from repository

    # filter by type=code
    repo_code = await student_client.get("/api/community/groups/repository?type=code")
    assert repo_code.status_code == 200
    for item in repo_code.json()["items"]:
        assert item["type"] == "code"


@pytest.mark.asyncio
async def test_like_unlike_group(database: AsyncSession, student_client: AsyncClient):
    cat = CommunityCategory(slug="cloud", name="云", order=1)
    database.add(cat)
    await database.flush()
    grp = CommunityGroup(title="云计算组", summary="Cloud", category_id=cat.id)
    database.add(grp)
    await database.commit()

    like_resp = await student_client.post(f"/api/community/groups/{grp.id}/like")
    assert like_resp.status_code == 200
    assert like_resp.json()["liked"] is True
    like_again = await student_client.post(f"/api/community/groups/{grp.id}/like")
    assert like_again.json()["liked"] is True

    unlike_resp = await student_client.delete(f"/api/community/groups/{grp.id}/like")
    assert unlike_resp.status_code == 200
    assert unlike_resp.json()["liked"] is False
    unlike_again = await student_client.delete(f"/api/community/groups/{grp.id}/like")
    assert unlike_again.json()["liked"] is False


@pytest.mark.asyncio
async def test_list_feed_and_invalid_group_id(
    database: AsyncSession, async_client: AsyncClient, student_client: AsyncClient, test_user: User
):
    cat = CommunityCategory(slug="ai", name="AI", order=1)
    database.add(cat)
    await database.flush()
    grp = CommunityGroup(title="AI组", summary="聊AI", category_id=cat.id)
    database.add(grp)
    await database.flush()
    # add posts directly
    p1 = CommunityPost(group_id=grp.id, user_id=test_user.id, title="帖子1", content="内容1")
    p2 = CommunityPost(group_id=grp.id, user_id=test_user.id, title="帖子2", content="内容2")
    database.add_all([p1, p2])
    await database.flush()  # ensure IDs
    # add attachments for repository filtering later
    a1 = CommunityPostAttachment(post_id=p1.id, type="document", url="http://doc", title="Doc")
    database.add(a1)
    await database.commit()

    # list feed latest
    feed_resp = await async_client.get("/api/community/groups/feed")
    assert feed_resp.status_code == 200
    assert feed_resp.json()["pagination"]["total"] >= 2

    # with group_id filter
    feed_group = await async_client.get(f"/api/community/groups/feed?group_id={grp.id}")
    assert feed_group.status_code == 200
    for item in feed_group.json()["items"]:
        assert item["group_id"] == grp.id

    # invalid group_id triggers 422
    invalid = await async_client.get("/api/community/groups/feed?group_id=abc")
    assert invalid.status_code == 422

    # repository invalid group_id
    invalid_repo = await async_client.get("/api/community/groups/repository?group_id=xyz")
    assert invalid_repo.status_code == 422
