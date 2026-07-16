from datetime import date

from pydantic import BaseModel


class ClickEventResponse(BaseModel):
    id: int
    url_id: int
    referrer: str
    ip_hash: str
    clicked_at: date
