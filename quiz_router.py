# from fastapi import APIRouter, Depends
# from pydantic import BaseModel
# from typing import Optional, Dict, Any, List
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, update
# from sqlalchemy.sql import func
# from typing import Optional, Literal
# from uuid import UUID
# import logging
# import json
# import uuid

# from database import SessionLocal
# from models import QuizAttempt, QuizAnswer, ProductClick
# from schemas import StartQuiz, SaveAnswer, SubmitQuiz, ProductClickSchema


# from quiz_engine import master_engine
# router = APIRouter()
# ENGINE_VERSION = "v1.0"

# LIFECYCLE_STAGE_BASE = {
#     "A": ["heat_combo", "whelping_kit", "extra_pads"],
#     "B": ["wifi_monitoring", "heat_combo", "extra_pads"],
#     "C": ["traction_pad", "add_on_room", "extra_pads"],
#     "D": ["add_on_room_next", "feeding_station", "mess_hall", "extra_pads"],
# }

# WINDOW_ELIGIBLE_STAGES = {"A", "B"}

# class JsonFormatter(logging.Formatter):
#     def format(self, record):
#         log_record = {
#             "timestamp": self.formatTime(record),
#             "level": record.levelname,
#             "logger": record.name,
#             "message": record.getMessage(),
#         }

#         if hasattr(record, "correlation_id"):
#             log_record["correlation_id"] = record.correlation_id

#         if record.exc_info:
#             log_record["exception"] = self.formatException(record.exc_info)

#         return json.dumps(log_record)


# logger = logging.getLogger("quiz_router")
# logger.setLevel(logging.INFO)

# console_handler = logging.StreamHandler()
# console_handler.setFormatter(JsonFormatter())
# logger.addHandler(console_handler)

# file_handler = logging.FileHandler("quiz_app.log")
# file_handler.setFormatter(JsonFormatter())
# logger.addHandler(file_handler)



# async def get_db():
#     async with SessionLocal() as session:
#         try:
#             yield session
#         finally:
#             await session.close()

# PRODUCT_CATALOG = {
#     "heat_combo": {"name": "Heat Combo", "url": "https://www.ezwhelp.com/products/heating-combo-for-classic-value-box-size-3838-or-4848?_pos=1&_psq=Heat+Combo&_ss=e&_v=1.0"},
#     "whelping_kit": {"name": "Whelping Kit", "url": "https://www.ezwhelp.com/products/whelping-kit?_pos=2&_psq=Whelping+Kit&_ss=e&_v=1.0"},
#     "corner_seat": {"name": "Corner Seat", "url": "https://www.ezwhelp.com/products/fab-box-corner-seat?_pos=1&_sid=eec2f2382&_ss=r"},
#     "acrylic_door": {"name": "Acrylic Door", "url": "https://www.ezwhelp.com/products/acrylic-glass-door-set-for-ezclassic-whelping-boxes?_pos=1&_psq=Acrylic+Door&_ss=e&_v=1.0"},
#     "heat_pad": {"name": "Heat Pad", "url": "https://www.ezwhelp.com/products/heat-pad-for-whelping-boxes?_pos=1&_psq=Heat+Pad&_ss=e&_v=1.0"},
#     "traction_pad": {"name": "Traction Pad", "url": "https://www.ezwhelp.com/products/ezwhelp-traction-pad?_pos=1&_psq=Traction+Pad&_ss=e&_v=1.0"},
# }

# PRODUCT_CATALOG.update({
#     "extra_pads": {
#         "name": "Extra Pads",
#         "url": "https://www.ezwhelp.com/products/black-white-slip-resistant-paw-print-pad-mat-2-pack"
#     },
#     "wifi_monitoring": {
#         "name": "WiFi Monitoring System",
#         "url": "https://www.ezwhelp.com/products/ezwhelp-smart-whelping-box-wifi-camera-temperature-monitoring-system"
#     },
#     "add_on_room": {
#         "name": "EZclassic Add-On Room",
#         "url": "https://www.ezwhelp.com/products/ezclassic-add-on-room"
#     },
#     "add_on_room_next": {
#         "name": "EZclassic Add-On Room (Expansion)",
#         "url": "https://www.ezwhelp.com/products/ezclassic-add-on-room"
#     },
#     "feeding_station": {
#         "name": "Feeding Station",
#         "url": "https://www.ezwhelp.com/products/feeding-station"
#     },
#     "mess_hall": {
#         "name": "EZclassic Mess Hall",
#         "url": "https://www.ezwhelp.com/products/ezclassic-mess-hall-add-on-room-set-standard-18-height"
#     },
# })


# BUNDLE_URLS = {
#     "starter": "https://www.ezwhelp.com/products/bundles-ezclassic-starter-set?_pos=1&_psq=Starter&_ss=e&_v=1.0",
#     "essential": "https://www.ezwhelp.com/products/bundles-ezclassic-basic-set?_pos=1&_psq=Essential&_ss=e&_v=1.0",
#     "pro": "https://www.ezwhelp.com/products/copy-of-bundles-ezclassic-pro-set?_pos=1&_psq=Pro&_ss=e&_v=1.0",
#     "elite": "https://www.ezwhelp.com/products/bundles-ezclassic-elite-set?_pos=1&_psq=Elite&_ss=e&_v=1.0",
#     "playyard": "https://www.ezwhelp.com/products/bundles-ezclassic-play-yard-set?_pos=1&_psq=Play+Yard&_ss=e&_v=1.0",
#     "condo": "https://www.ezwhelp.com/products/ezclassic-condo-bundle?_pos=1&_psq=Condo&_ss=e&_v=1.0&variant=51849455403380",
# }

# RULE_MATRIX = [
#     {"conditions": {"space": "C", "bundle_option": "A"}, "bundle": "condo"},
#     {"conditions": {"space": "C", "bundle_option": "B"}, "bundle": "playyard"},
#     {"conditions": {"space": "B", "bundle_option": "A"}, "bundle": "elite"},
#     {"conditions": {"space": "B", "bundle_option": "B"}, "bundle": "pro"},
#     {"conditions": {"space": "A", "bundle_option": "B"}, "bundle": "essential"},
#     {"conditions": {"space": "A", "bundle_option": "A"}, "bundle": "starter"},
# ]

# SIZE_MAP = {"A": 28, "B": 38, "C": 48}

# TIMELINE_MESSAGES = {
#     "A": "Get fully prepared before labor begins.",
#     "B": "Puppies arriving soon — prioritize readiness.",
#     "C": "Monitor newborns closely during first days.",
#     "D": "Support growing puppies safely.",
# }


# def structural_engine(data: Dict[str, Any]) -> Dict[str, Any]:
#     logger.info(f"Running structural engine with {data}")

#     for rule in RULE_MATRIX:
#         if all(data.get(k) == v for k, v in rule["conditions"].items()):
#             bundle = rule["bundle"]
#             break
#     else:
#         bundle = "starter"

#     box_size = SIZE_MAP.get(data.get("dam_size"))

#     if box_size == 28:
#         panel_height = '18"'
#     else:
#         panel_height = '28"' if data.get("panel_height") == "B" else '18"'

#     message = TIMELINE_MESSAGES.get(data["timeline"])

#     logger.info(f"Structural result bucket={bundle}")

#     return {
#         "bucket": bundle,
#         "bundle_url": BUNDLE_URLS[bundle],
#         "box_size_inches": box_size,
#         "panel_height": panel_height,
#         "timeline_message": message,
#         "recommended_products": []
#     }




# def existing_owner_engine(data: Dict[str, Any]) -> Dict[str, Any]:
#     logger.info(f"Running deterministic existing owner engine with {data}")

#     stage: str = data.get("stage")
#     has_window: str = data.get("has_window", "unknown")
#     box_height: str = data.get("box_height", "unknown")
#     due_date = data.get("due_date")

#     ENGINE_VERSION = "v1.0-lifecycle"

#     STAGE_BASE = {
#         "A": ["heat_combo", "whelping_kit", "extra_pads"],
#         "B": ["wifi_monitoring", "heat_combo", "extra_pads"],
#         "C": ["traction_pad", "add_on_room", "extra_pads"],
#         "D": ["add_on_room_next", "feeding_station", "mess_hall", "extra_pads"],
#     }

#     if stage not in STAGE_BASE:
#         logger.warning(f"Invalid stage received: {stage}")
#         return {
#             "bucket": "existing_owner",
#             "engine_version": ENGINE_VERSION,
#             "bundle_url": None,
#             "recommended_products": [],
#             "additional_products": [],
#             "timeline_message": "Invalid stage",
#             "height_message": "Unknown configuration."
#         }

#     product_keys = STAGE_BASE[stage].copy()

#     if stage in ["A", "B"] and has_window in ["no", "unknown"]:
#         product_keys.append("acrylic_door")

#     products = []
#     for key in product_keys:
#         if key in PRODUCT_CATALOG:
#             products.append(PRODUCT_CATALOG[key])
#         else:
#             logger.warning(f"Missing PRODUCT_CATALOG entry for key={key}")

#     MAX_VISIBLE = 3
#     primary_products = products[:MAX_VISIBLE]
#     additional_products = products[MAX_VISIBLE:]

#     if box_height == "18":
#         height_message = "Standard containment configuration."
#     elif box_height == "28":
#         height_message = "Tall configuration reduces containment urgency."
#     else:
#         height_message = "Height-neutral configuration."

#     if stage == "A" and due_date:
#         logger.info(f"Due date provided. Schedule reminders for {due_date}")

#     logger.info(
#         f"Lifecycle Engine | Stage={stage} | Window={has_window} "
#         f"| TotalProducts={len(products)}"
#     )

#     return {
#         "bucket": "existing_owner",
#         "engine_version": ENGINE_VERSION,
#         "bundle_url": None,
#         "recommended_products": primary_products,
#         "additional_products": additional_products,
#         "timeline_message": TIMELINE_MESSAGES.get(stage),
#         "height_message": height_message,
#     }


# def master_engine(data: Dict[str, Any]) -> Dict[str, Any]:
#     logger.info(f"Master engine routing path={data['path']}")

#     if data["path"] == "existing":
#         return existing_owner_engine(data)
#     else:
#         return structural_engine(data)


# class QuizInput(BaseModel):
#     attempt_id: UUID
#     path: str  
#     timeline: Optional[str] = None
#     space: Optional[str] = None
#     bundle_option: Optional[str] = None
#     dam_size: Optional[str] = None
#     panel_height: Optional[str] = None    
#     stage: Optional[Literal["A", "B", "C", "D"]] = None
#     has_window: Literal["yes", "no", "unknown"] = "unknown"
#     box_height: Literal["18", "28", "unknown"] = "unknown"
#     due_date: Optional[str] = None


# @router.post("/quiz")
# async def quiz(data: QuizInput, db: AsyncSession = Depends(get_db)):
#     # payload = data.dict()
#     payload = data.model_dump()
#     logger.info(f"Quiz payload received: {payload}")

#     result = master_engine(payload)

#     logger.info(
#         f"Computed result for attempt={data.attempt_id} "
#         f"bucket={result['bucket']}"
#     )

#     owns_box_flag = True if data.path == "existing" else False

#     await db.execute(
#         update(QuizAttempt)
#         .where(QuizAttempt.id == data.attempt_id)
#         # .values(
#         #     owns_box=owns_box_flag,
#         #     bucket=result["bucket"],
#         #     recommended_products=result,
#         # )
#         .values(
#         owns_box=owns_box_flag,
#         bucket=result["bucket"],
#         engine_version=result.get("engine_version"),
#         engine_result=result,
# )
#     )

#     await db.commit()

#     logger.info(
#         f"Persisted quiz result for attempt={data.attempt_id}"
#     )

#     return result
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
class QuizInput(BaseModel):
    attempt_id: UUID
    path: str

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
@router.post("/quiz")
async def quiz(data: QuizInput, db: AsyncSession = Depends(get_db)):
    payload = data.model_dump()
    logger.info(f"Quiz payload received: {payload}")

    # Run central engine
    result = master_engine(payload)

    logger.info(
        f"Engine result for attempt={data.attempt_id} "
        f"bucket={result.get('bucket')}"
    )

    owns_box_flag = data.path == "existing"

    # Persist result
    await db.execute(
        update(QuizAttempt)
        .where(QuizAttempt.id == data.attempt_id)
        .values(
            owns_box=owns_box_flag,
            bucket=result.get("bucket"),
            engine_version=result.get("engine_version"),
            engine_result=result,
        )
    )

    await db.commit()

    logger.info(f"Persisted quiz result for attempt={data.attempt_id}")

    return result