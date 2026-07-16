from datetime import date, timedelta

from pydantic import BaseModel, Field, field_validator, computed_field


class UrlRequest(BaseModel):
    owner_id: int = Field(..., description="User Id", ge=1)
    is_active: bool = Field(default=True)
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

    @computed_field
    @property
    def find_expire_at(self) -> date:
        expire_at = self.created_at + timedelta(weeks=7)

        return expire_at


class UrlResponse(BaseModel):
    id: int
    is_active: bool
    owner_id: int
    short_code: str
    created_at: date
