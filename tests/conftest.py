from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest_asyncio
from database import close_db, get_db, init_test_db
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.sql import get_db as get_sql_db
from app.main import app
from app.models.career import Career
from app.models.quiz import Option, Question, QuestionType, Quiz
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.services.auth_service import get_password_hash


@pytest_asyncio.fixture(scope="session")
async def database() -> AsyncGenerator[AsyncSession, None]:
    await init_test_db()
    try:
        async for db in get_db():
            yield db
    finally:
        await close_db()  # type:ignore


@pytest_asyncio.fixture
async def async_client(database: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        yield database

    app.dependency_overrides[get_sql_db] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_repo(database: AsyncSession) -> UserRepository:
    repo = UserRepository(database)
    return repo


@pytest_asyncio.fixture
async def test_user(user_repo: UserRepository) -> User:
    uuid = str(uuid4())
    hashed_password = get_password_hash("123456")
    user = await user_repo.create_user(
        username=f"test_{uuid}",
        password_hash=hashed_password,
        nickname="Test User",
        email=f"test_{uuid}@example.com",
        role=UserRole.user,
    )
    assert user
    return user


@pytest_asyncio.fixture
async def test_admin(user_repo: UserRepository) -> User:
    hashed_password = get_password_hash("123456")
    admin = await user_repo.create_user(
        username="test_admin",
        password_hash=hashed_password,
        nickname="Test Admin",
        email="test_admin@example.com",
        role=UserRole.admin,
    )
    assert admin
    return admin


@pytest_asyncio.fixture
async def admin_client(async_client: AsyncClient, test_admin: User) -> AsyncClient:
    response = await async_client.post(
        "/api/auth/login",
        data={"username": test_admin.username, "password": "123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = response.json()["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return async_client


@pytest_asyncio.fixture
async def student_client(async_client: AsyncClient, test_user: User) -> AsyncClient:
    response = None
    for password in ("123456", "newpassword"):
        login_response = await async_client.post(
            "/api/auth/login",
            data={"username": test_user.username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if login_response.status_code == 200:
            response = login_response
            break

    assert response is not None and response.status_code == 200
    access_token = response.json()["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return async_client


@pytest_asyncio.fixture
async def teacher_client(async_client: AsyncClient, test_teacher: User) -> AsyncClient:
    response = await async_client.post(
        "/api/auth/login",
        data={"username": test_teacher.username, "password": "123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = response.json()["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return async_client


@pytest_asyncio.fixture(scope="session")
async def sample_careers(database: AsyncSession) -> list[Career]:
    careers = [
        Career(
            name="工程实践工程师",
            description="擅长动手实践，负责工程设备的安装与维护。",
            holland_dimensions=["R", "I"],
            work_contents=["负责生产设备的调试", "制定日常维护计划"],
            required_skills="机械基础\n安全规范",
            core_competency_model={
                "basic_ability": 4,
                "self_management": 3,
                "task_execution": 3,
            },
            related_courses=["机械设计", "工程力学"],
            knowledge_background={
                "industry_knowledge": "了解制造业生产流程",
                "professional_knowledge": "掌握机械结构与维护原理",
            },
        ),
        Career(
            name="数据分析师",
            description="通过数据挖掘支持业务决策。",
            holland_dimensions=["I", "C"],
            work_contents=["构建数据报表", "进行探索性分析"],
            required_skills="SQL\n数据可视化",
            core_competency_model={
                "basic_ability": 4,
                "innovative_ability": 3,
                "task_execution": 3,
            },
            related_courses=["统计学", "概率论"],
            knowledge_background={
                "industry_knowledge": "了解数据驱动的业务模式",
                "professional_knowledge": "熟悉统计建模与数据库管理",
            },
        ),
        Career(
            name="创意设计师",
            description="专注视觉创意，为品牌打造设计方案。",
            holland_dimensions=["A", "E"],
            work_contents=["进行视觉概念设计", "与团队合作产出整合创意"],
            required_skills="视觉设计\n沟通表达",
            core_competency_model={
                "innovative_ability": 4,
                "social_ability": 3,
                "team_collaboration": 3,
            },
            related_courses=["视觉传达", "品牌策划"],
            knowledge_background={
                "industry_knowledge": "熟悉品牌推广流程",
                "professional_knowledge": "掌握平面与多媒体设计技能",
            },
        ),
        Career(
            name="教育顾问",
            description="提供学习规划与成长辅导。",
            holland_dimensions=["S", "E"],
            work_contents=["制定学习计划", "组织交流活动"],
            required_skills="学习规划\n心理辅导",
            core_competency_model={
                "social_ability": 4,
                "team_collaboration": 3,
                "self_management": 3,
            },
            related_courses=["教育心理学", "教学设计"],
            knowledge_background={
                "industry_knowledge": "了解教育培训行业趋势",
                "professional_knowledge": "熟悉教学方法与评估工具",
            },
        ),
    ]
    database.add_all(careers)
    await database.commit()
    for career in careers:
        await database.refresh(career)
    return careers


@pytest_asyncio.fixture
async def sample_quiz(database: AsyncSession, sample_careers: list[Career]) -> Quiz:
    quiz = Quiz(
        title="职业兴趣测评",
        description="基础霍兰德测评",
        is_published=True,
        config={"slug": "test-classic"},
    )
    database.add(quiz)
    await database.flush()

    questions = [
        Question(
            quiz_id=quiz.id,
            title="场景判断",
            content="面对需要动手实践的任务，你的选择是？",
            question_type=QuestionType.classic_scenario,
            order=1,
        ),
        Question(
            quiz_id=quiz.id,
            title="兴趣偏好",
            content="以下哪类活动更吸引你？",
            question_type=QuestionType.word_choice,
            order=2,
        ),
        Question(
            quiz_id=quiz.id,
            title="价值排序",
            content="你更看重哪种工作价值？",
            question_type=QuestionType.value_balance,
            order=3,
        ),
    ]

    database.add_all(questions)
    await database.flush()

    options = [
        Option(question_id=questions[0].id, content="立即动手尝试解决", dimension="R", score=5, order=1),
        Option(question_id=questions[0].id, content="查阅资料后再动手", dimension="I", score=3, order=2),
        Option(question_id=questions[1].id, content="参加创意工作坊", dimension="A", score=5, order=1),
        Option(question_id=questions[1].id, content="组织同学一起做项目", dimension="E", score=4, order=2),
        Option(question_id=questions[2].id, content="帮助他人成长", dimension="S", score=5, order=1),
        Option(question_id=questions[2].id, content="处理数据确保准确", dimension="C", score=4, order=2),
    ]

    database.add_all(options)
    await database.commit()
    await database.refresh(quiz)
    return quiz
