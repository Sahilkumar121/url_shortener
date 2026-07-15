from datetime import date

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date

from app.database import Base


class Url(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    short_code = Column(String, nullable=False, unique=True)
    long_url = Column(String, nullable=False)
    created_at = Column(Date, default=date.today)
    expires_at = Column(Date)
