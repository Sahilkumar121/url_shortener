from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.urls import Url
from app.schemas.url import UrlRequest, UrlResponse
from app.utils.short_code import generate_short_code

from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_hash_password

route = APIRouter(prefix="/url")


@route.post("/", response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
async def post_url(url_request: UrlRequest, db: AsyncSession = Depends(get_db)):
    # 1. check if the user has already shortened the url
    stmt = select(Url).where(
        Url.long_url == url_request.long_url, Url.owner_id == url_request.owner_id
    )
    result = await db.execute(stmt)
    existing_url = result.scalar_one_or_none()

    if existing_url:
        return existing_url

    # 2. generate 6 digits random short code
    short_code = None
    for _ in range(5):
        potential_code = generate_short_code()
        code_stmt = select(Url).where(Url.short_code == potential_code)
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
        owner_id=url_request.owner_id,
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

@route.post('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm, db = Depends(get_db)):
    user_exist = db.get_user(username=form_data.username)
    
    if not user_exist and not verify_hash_password(form_data.password, user_exist.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Username and Password")