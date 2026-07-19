from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Date, UniqueConstraint

from app.database import Base
from datetime import datetime, timezone


class ClickEvent(Base):
    __tablename__ = "click_event"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, nullable=False
    )
    url_id: Mapped[int] = mapped_column(Integer, ForeignKey("urls.id"))
    referer: Mapped[str] = mapped_column(String, nullable=False)
    ip_hash: Mapped[str] = mapped_column(String, nullable=False)
    clicked_at: Mapped[Date] = mapped_column(
        Date, default=datetime.now(timezone.utc), nullable=False
    )

    __table_args__ = UniqueConstraint("url_id", "ip_hash", "uq_url_id_ip_hash")
