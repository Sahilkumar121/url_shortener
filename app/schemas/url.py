from datetime import date, timedelta

from pydantic import BaseModel, Field, field_validator, computed_field

from typing import List, Optional


class UrlRequest(BaseModel):
    long_url: str = Field(..., description="Provide the Url")
    is_active: bool = Field(default=True)
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


class UrlBulkRequest(BaseModel):
    long_url: List[str] = Field(
        ...,
        description="List of url",
        examples=["http://example.com", "http://google.com"],
    )
    created_at: date = Field(default_factory=date.today)

    @computed_field
    @property
    def find_expire_at(self) -> date:
        expire_at = self.created_at + timedelta(weeks=7)

        return expire_at


class UrlUpdateRedquest(BaseModel):
    owner_id: Optional[int] = None
    long_url: Optional[str] = None
    created_at: Optional[date] = None
    is_active: Optional[bool] = None


class UrlResponse(BaseModel):
    id: int
    is_active: bool
    owner_id: int
    short_code: str
    created_at: date
