

from sqlalchemy import Column, Integer, String, ForeignKey, Date

from app.database import Base

class ClickEvent(Base):
    __tablename__ = "click_event"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    url_id = Column(Integer, ForeignKey("urls.id"))
    referrer = Column(String, nullable=False)
    ip_hash = Column(String, unique=True, nullable=False)
    clicked_at = Column(Date, nullable=False)