import pytest
from httpx import AsyncClient
from sqlalchemy import select
from uuid import UUID

from main import app
from models import QuizAttempt, QuizAnswer, ProductClick


pytestmark = pytest.mark.anyio


# ---------------------------------
# Full Quiz Flow Integration Test
# ---------------------------------
async def test_full_quiz_flow(async_session):

 
    from httpx import AsyncClient
    from httpx import ASGITransport

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        # ---------------------------
        # 1️⃣ Start Quiz
        # ---------------------------
        start_response = await client.post(
            "/start-quiz",
            json={"path": "existing"}
        )

        assert start_response.status_code == 200
        attempt_id = start_response.json()["attempt_id"]
        assert UUID(attempt_id)

        # Verify attempt exists in DB
        result = await async_session.execute(
            select(QuizAttempt).where(QuizAttempt.id == attempt_id)
        )
        attempt = result.scalar_one()
        assert attempt.path == "existing"
        assert attempt.is_completed is False

        # ---------------------------
        # 2️⃣ Save Answer
        # ---------------------------
        save_response = await client.post(
            "/save-answer",
            json={
                "attempt_id": attempt_id,
                "question_id": "q1",
                "answer_key": "A"
            }
        )

        assert save_response.status_code == 200
        assert save_response.json()["status"] == "saved"

        # Verify answer persisted
        result = await async_session.execute(
            select(QuizAnswer).where(QuizAnswer.attempt_id == attempt_id)
        )
        answer = result.scalar_one()
        assert answer.question_id == "q1"

        # ---------------------------
        # 3️⃣ Compute Result
        # ---------------------------
        quiz_response = await client.post(
            "/quiz",
            json={
                "attempt_id": attempt_id,
                "path": "existing",
                "stage": "A",
                "has_window": "no",
                "box_height": "18"
            }
        )

        assert quiz_response.status_code == 200
        data = quiz_response.json()

        assert data["bucket"] == "existing_owner"
        assert "recommended_products" in data

        # Verify result persisted
        result = await async_session.execute(
            select(QuizAttempt).where(QuizAttempt.id == attempt_id)
        )
        attempt = result.scalar_one()
        assert attempt.bucket == "existing_owner"
        assert attempt.engine_result is not None

        # ---------------------------
        # 4️⃣ Submit Quiz
        # ---------------------------
        submit_response = await client.post(
            "/submit-quiz",
            json={"attempt_id": attempt_id}
        )

        assert submit_response.status_code == 200
        assert submit_response.json()["status"] == "completed"

        # Verify completion flag
        result = await async_session.execute(
            select(QuizAttempt).where(QuizAttempt.id == attempt_id)
        )
        attempt = result.scalar_one()
        assert attempt.is_completed is True
        assert attempt.submitted_at is not None

        # ---------------------------
        # 5️⃣ Product Click
        # ---------------------------
        click_response = await client.post(
            "/product-click",
            json={
                "attempt_id": attempt_id,
                "product_id": "heat_combo",
                "position": 1
            }
        )

        assert click_response.status_code == 200
        assert click_response.json()["status"] == "tracked"

        # Verify click stored
        result = await async_session.execute(
            select(ProductClick).where(ProductClick.attempt_id == attempt_id)
        )
        click = result.scalar_one()
        assert click.product_id == "heat_combo"
        assert click.position == 1