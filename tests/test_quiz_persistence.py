import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from main import app
from database import SessionLocal
from models import QuizAttempt


@pytest.mark.anyio
async def test_existing_owner_engine_persistence():

    # 1️⃣ Create a quiz attempt row first
    attempt_id = uuid.uuid4()

    async with SessionLocal() as session:
        attempt = QuizAttempt(
            id=attempt_id,
            path="existing",
            owns_box=True,
        )
        session.add(attempt)
        await session.commit()

    # 2️⃣ Call the API (FIXED PART HERE)
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/quiz",
            json={
                "attempt_id": str(attempt_id),
                "path": "existing",
                "stage": "A",
                "has_window": "yes",
                "box_height": "18",
            },
        )

    assert response.status_code == 200

    body = response.json()

    # 3️⃣ Validate API response structure
    assert body["bucket"] == "existing_owner"
    assert "engine_version" in body
    assert body["engine_version"] == "v1.0-lifecycle"
    assert len(body["recommended_products"]) > 0

    # 4️⃣ Validate DB persistence
    async with SessionLocal() as session:
        result = await session.execute(
            select(QuizAttempt).where(QuizAttempt.id == attempt_id)
        )
        db_attempt = result.scalar_one()

        assert db_attempt.engine_version == "v1.0-lifecycle"
        assert db_attempt.engine_result is not None
        assert db_attempt.engine_result["bucket"] == "existing_owner"
        assert len(db_attempt.engine_result["recommended_products"]) > 0