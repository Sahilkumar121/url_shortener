from datetime import date

from pydantic import BaseModel, Field, field_validator


class Url(BaseModel):
    owner_id: int = Field(..., description="User Id", ge=1)
    long_url: str = Field(..., description="Provide the Url")
    created_at: date = Field(default_factory=date.today)

    @field_validator("created_at")
    @classmethod
    def check_date_range(cls, value: date) -> date:
        if value < date(1990, 1, 1):
            raise ValueError("Date cannot be before 1990-1-1")

        if value > date.today():
            raise ValueError("Date cannot be in the future")

        return value
