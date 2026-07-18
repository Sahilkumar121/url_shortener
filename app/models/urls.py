from datetime import date

from sqlalchemy import Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    short_code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    long_url: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[date] = mapped_column(Date, default=date.today)
    expires_at: Mapped[date] = mapped_column(Date)
