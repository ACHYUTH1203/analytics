from pydantic import BaseModel
from uuid import UUID

class StartQuiz(BaseModel):
    path: str


class SaveAnswer(BaseModel):
    attempt_id: UUID
    question_id: str
    answer_key: str


class SubmitQuiz(BaseModel):
    attempt_id: UUID


class ProductClickSchema(BaseModel):
    attempt_id: UUID
    product_id: str
    position: int