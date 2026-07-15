from datetime import date

from sqlalchemy import Column, Integer, String, Boolean, Date

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(Date, default=date.today)
