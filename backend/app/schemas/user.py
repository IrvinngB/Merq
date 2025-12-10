from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import re


def validate_username(value: str) -> str:
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', value):
        raise ValueError('Username debe tener 3-20 caracteres alfanuméricos o guion bajo')
    return value.lower()


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    role: str = "student"

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if isinstance(obj, dict) and 'username' in obj:
            obj['username'] = validate_username(obj['username'])
        return super().model_validate(obj, **kwargs)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=20)
    password: str | None = Field(None, min_length=6)
    full_name: str | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
