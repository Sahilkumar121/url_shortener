from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models.urls import Url
from app.models.users import User
from app.schemas.url import UrlRequest, UrlResponse
from app.utils.short_code import generate_short_code

route = APIRouter(prefix="/url", tags=["Url"])


@route.get("/me")
async def get_my_url(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Url).where(Url.owner_id == current_user.id)
    user_result = await db.execute(stmt)

    user_urls = user_result.scalars().all()

    return user_urls


@route.post("/", response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
async def post_url(url_request: UrlRequest, db: AsyncSession = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    # 1. check if the user has already shortened the url
    stmt = (
        select(Url)
        .where(Url.long_url == url_request.long_url)
        .where(Url.owner_id == url_request.owner_id)
    )
    result = await db.execute(stmt)
    existing_url = result.scalar_one_or_none()

    if existing_url:
        return existing_url

    # 2. generate 6 digits random short code
    short_code = None
    for _ in range(5):
        potential_code = generate_short_code()
        code_stmt = select(Url).where(ColumnElement(Url.short_code == potential_code))
        code_result = await db.execute(code_stmt)
        code_exists = code_result.scalar_one_or_none()

        if not code_exists:
            short_code = potential_code
            break

    if not short_code:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate short code Try Again Later",
        )

    database_url = Url(
        owner_id=current_user.id,
        short_code=short_code,
        is_active=url_request.is_active,
        created_at=url_request.created_at,
        expires_at=url_request.find_expire_at,
        long_url=url_request.long_url,
    )

    db.add(database_url)
    await db.commit()
    await db.refresh(database_url)

    return database_url
