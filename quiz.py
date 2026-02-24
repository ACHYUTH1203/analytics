from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from database import SessionLocal
from models import QuizAttempt, QuizAnswer, ProductClick
from schemas import StartQuiz, SaveAnswer, SubmitQuiz, ProductClickSchema

router = APIRouter(prefix="/quiz")

async def get_db():
    async with SessionLocal() as session:
        yield session


@router.post("/start")
async def start_quiz(data: StartQuiz, db: AsyncSession = Depends(get_db)):
    attempt = QuizAttempt(path=data.path)
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    return {"attempt_id": attempt.id}


@router.post("/answer")
async def save_answer(data: SaveAnswer, db: AsyncSession = Depends(get_db)):
    answer = QuizAnswer(
        attempt_id=data.attempt_id,
        question_id=data.question_id,
        answer_key=data.answer_key,
    )
    db.add(answer)
    await db.commit()
    return {"message": "Answer saved"}


@router.post("/submit")
async def submit_quiz(data: SubmitQuiz, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(QuizAttempt).where(QuizAttempt.id == data.attempt_id)
    )
    attempt = result.scalar_one_or_none()

    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    attempt.is_completed = True
    attempt.submitted_at = datetime.utcnow()
    await db.commit()

    return {"message": "Quiz submitted"}


@router.post("/product-click")
async def product_click(data: ProductClickSchema, db: AsyncSession = Depends(get_db)):
    click = ProductClick(
        attempt_id=data.attempt_id,
        product_id=data.product_id,
        position=data.position,
    )
    db.add(click)
    await db.commit()

    return {"message": "Click tracked"}