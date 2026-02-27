import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey,Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from database import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path = Column(String)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True))
    is_completed = Column(Boolean, default=False)
    owns_box = Column(Boolean)
    bucket = Column(String)

    engine_version = Column(String)
    engine_result = Column(JSON)

class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("quiz_attempts.id"))
    question_id = Column(String)
    answer_key = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ProductClick(Base):
    __tablename__ = "product_clicks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("quiz_attempts.id"))
    product_id = Column(String)
    position = Column(Integer)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())