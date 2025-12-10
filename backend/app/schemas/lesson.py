from pydantic import BaseModel
from datetime import datetime


class LessonCreate(BaseModel):
    title: str
    content: str | None = None


class LessonUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    position: int | None = None


class LessonResponse(BaseModel):
    id: int
    title: str
    content: str | None = None
    position: int
    module_id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
