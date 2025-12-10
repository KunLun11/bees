from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            msg = "Username must be at least 3 characters"
            raise ValueError(msg)
        if len(v) > 50:
            msg = "Username must be less than 50 characters"
            raise ValueError(msg)
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            msg = "Password must be at least 8 characters"
            raise ValueError(msg)
        return v


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    id: int
    email: str
    username: str

    model_config = ConfigDict(from_attributes=True)
