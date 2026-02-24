from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.sql import func
import logging
import json
import time
import uuid

from database import SessionLocal
from models import QuizAttempt, QuizAnswer, ProductClick
from schemas import StartQuiz, SaveAnswer, SubmitQuiz, ProductClickSchema

router = APIRouter()


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


console_handler = logging.StreamHandler()
console_handler.setFormatter(JsonFormatter())
logger.addHandler(console_handler)


file_handler = logging.FileHandler("quiz_app.log")
file_handler.setFormatter(JsonFormatter())
logger.addHandler(file_handler)





async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            logger.exception("Database session error")
            raise
        finally:
            await session.close()




BUNDLE_URLS = {
    "starter": "https://www.ezwhelp.com/products/bundles-ezclassic-starter-set?_pos=1&_psq=Starter&_ss=e&_v=1.0",
    "essential": "https://www.ezwhelp.com/products/bundles-ezclassic-basic-set?_pos=1&_psq=Essential&_ss=e&_v=1.0",
    "pro": "https://www.ezwhelp.com/products/copy-of-bundles-ezclassic-pro-set?_pos=1&_psq=Pro&_ss=e&_v=1.0",
    "elite": "https://www.ezwhelp.com/products/bundles-ezclassic-elite-set?_pos=1&_psq=Elite&_ss=e&_v=1.0",
    "playyard": "https://www.ezwhelp.com/products/bundles-ezclassic-play-yard-set?_pos=1&_psq=Play+Yard&_ss=e&_v=1.0",
    "condo": "https://www.ezwhelp.com/products/ezclassic-condo-bundle?_pos=1&_psq=Condo&_ss=e&_v=1.0&variant=51849455403380",
}

RULE_MATRIX = [
    {"conditions": {"space": "C", "bundle_option": "A"}, "bundle": "condo"},
    {"conditions": {"space": "C", "bundle_option": "B"}, "bundle": "playyard"},
    {"conditions": {"space": "B", "bundle_option": "A"}, "bundle": "elite"},
    {"conditions": {"space": "B", "bundle_option": "B"}, "bundle": "pro"},
    {"conditions": {"space": "A", "bundle_option": "B"}, "bundle": "essential"},
    {"conditions": {"space": "A", "bundle_option": "A"}, "bundle": "starter"},
]

def matches(rule_conditions: Dict[str, Any], data: Dict[str, Any]) -> bool:
    return all(data.get(k) == v for k, v in rule_conditions.items())

def route_bundle(data: Dict[str, Any]) -> str:
    logger.info(f"Routing bundle with {data}")
    for rule in RULE_MATRIX:
        if matches(rule["conditions"], data):
            logger.info(f"Matched rule {rule['conditions']} → {rule['bundle']}")
            return rule["bundle"]
    logger.warning("No rule matched. Defaulting to starter.")
    return "starter"

SIZE_MAP = {"A": 28, "B": 38, "C": 48}

TIMELINE_MESSAGES = {
    "A": "Get fully prepared before labor begins.",
    "B": "Puppies arriving soon — prioritize readiness.",
    "C": "Monitor newborns closely during first days.",
    "D": "Support growing puppies safely.",
}




class QuizInput(BaseModel):
    timeline: str
    experience: str
    space: str
    bundle_option: str
    dam_size: str
    panel_height: Optional[str] = None


@router.post("/quiz")
async def quiz(data: QuizInput):

    logger.info(f"Quiz payload received: {data.dict()}")

    bundle_key = route_bundle({
        "space": data.space,
        "bundle_option": data.bundle_option
    })

    box_size = SIZE_MAP.get(data.dam_size)

    if box_size == 28:
        final_panel_height = '18"'
    else:
        final_panel_height = '28"' if data.panel_height == "B" else '18"'

    timeline_message = TIMELINE_MESSAGES.get(
        data.timeline,
        "Choose the best setup for your litter."
    )

    logger.info(
        f"Quiz result bundle={bundle_key}, "
        f"box_size={box_size}, panel_height={final_panel_height}"
    )

    return {
        "bundle": bundle_key,
        "bundle_url": BUNDLE_URLS[bundle_key],
        "box_size_inches": box_size,
        "panel_height": final_panel_height,
        "timeline_message": timeline_message
    }




@router.post("/start-quiz")
async def start_quiz(data: StartQuiz, db: AsyncSession = Depends(get_db)):

    logger.info(f"Starting quiz path={data.path}")

    attempt = QuizAttempt(path=data.path)
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)

    logger.info(f"Quiz started id={attempt.id}")

    return {
        "attempt_id": attempt.id,
        "started_at": attempt.started_at
    }


@router.post("/save-answer")
async def save_answer(data: SaveAnswer, db: AsyncSession = Depends(get_db)):

    logger.info(
        f"Saving answer attempt={data.attempt_id} "
        f"question={data.question_id}"
    )

    result = await db.execute(
        select(QuizAnswer).where(
            QuizAnswer.attempt_id == data.attempt_id,
            QuizAnswer.question_id == data.question_id
        )
    )

    existing = result.scalars().first()

    if existing:
        existing.answer_key = data.answer_key
    else:
        db.add(QuizAnswer(**data.dict()))

    await db.commit()
    return {"status": "saved"}


@router.post("/submit-quiz")
async def submit_quiz(data: SubmitQuiz, db: AsyncSession = Depends(get_db)):

    logger.info(f"Submitting quiz attempt={data.attempt_id}")

    await db.execute(
        update(QuizAttempt)
        .where(QuizAttempt.id == data.attempt_id)
        .values(is_completed=True, submitted_at=func.now())
    )

    await db.commit()
    return {"status": "completed"}


@router.post("/product-click")
async def product_click(data: ProductClickSchema, db: AsyncSession = Depends(get_db)):

    logger.info(
        f"Product click attempt={data.attempt_id} "
        f"product={data.product_id} position={data.position}"
    )

    db.add(ProductClick(**data.dict()))
    await db.commit()

    return {"status": "tracked"}