import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

pytest.importorskip("aiosqlite")

from app import main
from app.database import get_session
from app.models import Base, QuestionType, RubricStrictness, User, UserRole


@pytest.fixture(scope="module")
def test_client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_init_db() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    main.init_db = override_init_db

    loop = asyncio.get_event_loop()
    loop.run_until_complete(override_init_db())

    async def override_get_session():
        async with async_session() as session:
            yield session

    main.app.dependency_overrides[get_session] = override_get_session
    client = TestClient(main.app)

    yield {"client": client, "sessionmaker": async_session, "loop": loop}

    client.close()
    main.app.dependency_overrides.clear()
    loop.run_until_complete(engine.dispose())


@pytest.fixture(scope="module")
def teacher_id(test_client):
    sessionmaker = test_client["sessionmaker"]
    loop = test_client["loop"]

    async def _create_teacher():
        async with sessionmaker() as session:
            user = User(name="Teacher", email="teacher@example.com", role=UserRole.TEACHER)
            session.add(user)
            await session.commit()
            return user.id

    return loop.run_until_complete(_create_teacher())


@pytest.fixture(scope="module")
def created_exam_id(test_client, teacher_id):
    client = test_client["client"]
    response = client.post(
        "/api/exams",
        json={
            "title": "Math Finals",
            "description": "Algebra and geometry",
            "created_by": str(teacher_id),
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_create_exam_endpoint(test_client, teacher_id):
    client = test_client["client"]
    response = client.post(
        "/api/exams",
        json={
            "title": "Physics",
            "description": "Mechanics",
            "created_by": str(teacher_id),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Physics"
    assert data["description"] == "Mechanics"
    assert data["created_by"] == str(teacher_id)


def test_add_questions(test_client, created_exam_id):
    client = test_client["client"]
    question_payload = [
        {"question_number": 1, "type": QuestionType.MCQ.value, "marks": 5, "text": "Q1"},
        {"question_number": 2, "type": QuestionType.SHORT.value, "marks": 10, "text": "Q2"},
    ]

    response = client.post(f"/api/exams/{created_exam_id}/questions", json=question_payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(item["exam_id"] == created_exam_id for item in data)
    assert {item["question_number"] for item in data} == {1, 2}


def test_add_rubric(test_client, created_exam_id):
    client = test_client["client"]
    question_payload = [
        {"question_number": 3, "type": QuestionType.LONG.value, "marks": 15, "text": "Explain"}
    ]
    question_response = client.post(
        f"/api/exams/{created_exam_id}/questions",
        json=question_payload,
    )
    question_id = question_response.json()[0]["id"]

    rubric_payload = {
        "key_points": {"steps": ["a", "b"]},
        "marking_scheme": {"correct": 10},
        "strictness": RubricStrictness.NEUTRAL.value,
    }

    response = client.post(f"/api/questions/{question_id}/rubric", json=rubric_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["question_id"] == question_id
    assert data["strictness"] == RubricStrictness.NEUTRAL.value
    assert data["key_points"] == rubric_payload["key_points"]
