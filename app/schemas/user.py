from datetime import date

from pydantic import BaseModel, Field, field_validator, EmailStr

from typing import Optional


class UserRequest(BaseModel):
    email: EmailStr = Field(..., min_length=11)
    password: str = Field(..., max_length=20)
    is_admin: bool = Field(default=False, description="Are you admin yes/no ?")
    created_at: date = Field(default_factory=date.today)

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        domain_name = value.split("@")[-1]

        if domain_name not in ["gmail.com"]:
            raise ValueError("Not a Valid Email")
        return value

    @field_validator("password")
    @classmethod
    def check_password(cls, value: str) -> str:
        if not value.isalnum():
            raise ValueError("Not a Valid Password")

        return value

    @field_validator("created_at")
    @classmethod
    def check_date_range(cls, value: date) -> date:
        if value < date(1990, 1, 1):
            raise ValueError("Date cannot be before 1990-1-1")

        if value > date.today():
            raise ValueError("Date cannot be in the future")

        return value


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    is_admin: Optional[bool] = None
    created_at: Optional[date] = None


class UserResponse(BaseModel):
    id: int
    email: str
    is_admin: bool
    created_at: date
