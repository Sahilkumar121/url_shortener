from fastapi import APIRouter, Depends, Request, Header, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.core.security import generate_hash_ip
from app.models.click_events import ClickEvent
from app.models.urls import Url


route = APIRouter(prefix="/redirect", tags=["Redirect"])


@route.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    referer: str | None = Header(default=None),
):
    stmt = select(Url).where(Url.short_code == short_code)
    url_result = await db.execute(stmt)
    url_exist = url_result.scalar_one_or_none()

    if not url_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Url Do Not Exist"
        )

    raw_ip = request.client.host if request.client else "Unknown"

    ip_hash = generate_hash_ip(raw_ip)
    safe_referer = referer or "Digest"

    new_click = ClickEvent(
        url_id=url_exist.id,
        referer=safe_referer,
        ip_hash=ip_hash,
    )

    try:
        db.add(new_click)
        await db.commit()
        await db.refresh(new_click)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There is error {e}",
        )

    return {
        "success": True,
        "message": "Clicked Recorded",
        "long_url": url_exist.long_url,
    }
