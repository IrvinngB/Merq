from pydantic import BaseModel
from datetime import datetime


class ModuleCreate(BaseModel):
    title: str
    description: str | None = None


class ModuleUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    position: int | None = None


class ModuleResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    position: int
    course_id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
