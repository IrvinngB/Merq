from pydantic import BaseModel
from datetime import datetime


class OptionCreate(BaseModel):
    text: str
    is_correct: bool = False


class OptionUpdate(BaseModel):
    text: str | None = None
    is_correct: bool | None = None


class OptionResponse(BaseModel):
    id: int
    text: str
    is_correct: bool
    question_id: int

    model_config = {"from_attributes": True}


class QuestionCreate(BaseModel):
    text: str
    question_type: str = "multiple_choice"
    difficulty: str = "medium"
    options: list[OptionCreate] | None = None


class QuestionUpdate(BaseModel):
    text: str | None = None
    question_type: str | None = None
    difficulty: str | None = None


class QuestionResponse(BaseModel):
    id: int
    text: str
    question_type: str
    difficulty: str
    lesson_id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class QuestionWithOptions(QuestionResponse):
    options: list[OptionResponse] = []
