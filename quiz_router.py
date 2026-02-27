
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from uuid import UUID
import logging
import json

from database import SessionLocal
from models import QuizAttempt
from quiz_engine import master_engine


# -----------------------
# Router Setup
# -----------------------
router = APIRouter()


# -----------------------
# Structured JSON Logger
# -----------------------
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "correlation_id"):
            log_record["correlation_id"] = record.correlation_id

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


logger = logging.getLogger("quiz_router")
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JsonFormatter())
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler("quiz_app.log")
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)


# -----------------------
# DB Dependency
# -----------------------
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# -----------------------
# Request Schema
# -----------------------
from uuid import uuid4
class QuizInput(BaseModel):
    attempt_id: Optional[UUID] = None
    path: Optional[str] = "new"

    # Structural flow
    timeline: Optional[str] = None
    space: Optional[str] = None
    bundle_option: Optional[str] = None
    dam_size: Optional[str] = None
    panel_height: Optional[str] = None

    # Existing owner flow
    stage: Optional[Literal["A", "B", "C", "D"]] = None
    has_window: Literal["yes", "no", "unknown"] = "unknown"
    box_height: Literal["18", "28", "unknown"] = "unknown"
    due_date: Optional[str] = None

# -----------------------
# Quiz Endpoint
# -----------------------
# @router.post("/quiz")
# async def quiz(data: QuizInput, db: AsyncSession = Depends(get_db)):
#     payload = data.model_dump()
#     logger.info(f"Quiz payload received: {payload}")

#     # Run central engine
#     result = master_engine(payload)

#     logger.info(
#         f"Engine result for attempt={data.attempt_id} "
#         f"bucket={result.get('bucket')}"
#     )

#     owns_box_flag = data.path == "existing"

#     # Persist result
#     await db.execute(
#         update(QuizAttempt)
#         .where(QuizAttempt.id == data.attempt_id)
#         .values(
#             owns_box=owns_box_flag,
#             bucket=result.get("bucket"),
#             engine_version=result.get("engine_version"),
#             engine_result=result,
#         )
#     )

#     await db.commit()

#     logger.info(f"Persisted quiz result for attempt={data.attempt_id}")

#     return result




@router.post("/quiz")
async def quiz(data: QuizInput, db: AsyncSession = Depends(get_db)):

    # -----------------------------
    # Auto-create attempt if missing
    # -----------------------------
    if not data.attempt_id:
        new_attempt = QuizAttempt(
            id=uuid4(),
            path=data.path or "new",
            is_completed=False
        )

        db.add(new_attempt)
        await db.commit()
        await db.refresh(new_attempt)

        attempt_id = new_attempt.id
    else:
        attempt_id = data.attempt_id

    payload = data.model_dump()
    payload["attempt_id"] = attempt_id
    payload["path"] = data.path or "new"

    # Run engine
    result = master_engine(payload)

    # Persist result
    await db.execute(
        update(QuizAttempt)
        .where(QuizAttempt.id == attempt_id)
        .values(
            owns_box=(payload["path"] == "existing"),
            bucket=result.get("bucket"),
            engine_version=result.get("engine_version"),
            engine_result=result,
        )
    )

    await db.commit()

    return {
        "attempt_id": attempt_id,
        **result
    }

from sqlalchemy import insert
from models import QuizAttempt
from schemas import StartQuiz

@router.post("/start-quiz")
async def start_quiz(data: StartQuiz, db: AsyncSession = Depends(get_db)):
    if data.path == "existing":
        final_path = "existing"
    else:
        final_path = "new"

    new_attempt = QuizAttempt(
        path=final_path,
        is_completed=False
    )

    db.add(new_attempt)
    await db.commit()
    await db.refresh(new_attempt)

    return {"attempt_id": new_attempt.id}

from models import QuizAnswer
from schemas import SaveAnswer

@router.post("/save-answer")
async def save_answer(data: SaveAnswer, db: AsyncSession = Depends(get_db)):
    answer = QuizAnswer(
        attempt_id=data.attempt_id,
        question_id=data.question_id,
        answer_key=data.answer_key
    )

    db.add(answer)
    await db.commit()

    return {"status": "saved"}


from sqlalchemy.sql import func
from schemas import SubmitQuiz

@router.post("/submit-quiz")
async def submit_quiz(data: SubmitQuiz, db: AsyncSession = Depends(get_db)):
    await db.execute(
        update(QuizAttempt)
        .where(QuizAttempt.id == data.attempt_id)
        .values(
            is_completed=True,
            submitted_at=func.now()
        )
    )

    await db.commit()

    return {"status": "completed"}

from models import ProductClick
from schemas import ProductClickSchema

@router.post("/product-click")
async def product_click(data: ProductClickSchema, db: AsyncSession = Depends(get_db)):
    click = ProductClick(
        attempt_id=data.attempt_id,
        product_id=data.product_id,
        position=data.position
    )

    db.add(click)
    await db.commit()

    return {"status": "tracked"}