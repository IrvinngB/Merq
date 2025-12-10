from pydantic import BaseModel
from datetime import datetime


class CourseCreate(BaseModel):
    title: str
    description: str | None = None


class CourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_published: bool | None = None


class CourseResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    is_published: bool
    teacher_id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
