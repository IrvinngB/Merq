from pydantic import BaseModel
from datetime import datetime


class EnrollmentCreate(BaseModel):
    course_id: int


class ProgressUpdate(BaseModel):
    progress_percentage: int


class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    status: str
    progress_percentage: int
    enrolled_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}
