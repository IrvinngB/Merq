from pydantic import BaseModel
from datetime import datetime


class AttemptCreate(BaseModel):
    question_id: int
    selected_option_id: int | None = None
    answer_text: str | None = None
    response_time_seconds: float | None = None


class AttemptResponse(BaseModel):
    id: int
    student_id: int
    question_id: int
    selected_option_id: int | None = None
    answer_text: str | None = None
    is_correct: bool
    response_time_seconds: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentStats(BaseModel):
    total_attempts: int
    correct_attempts: int
    accuracy_rate: float
    average_response_time: float | None = None


class QuestionStats(BaseModel):
    total_attempts: int
    correct_attempts: int
    success_rate: float
