from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models.urls import Url
from app.models.users import User
from app.schemas.url import UrlRequest, UrlResponse, UrlBulkRequest, UrlUpdateRedquest
from app.services.shortner import generate_unique_code
from app.utils.qrcode import generate_qr_code

route = APIRouter(prefix="/url", tags=["Url"])


@route.get("/me")
async def get_my_url(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    stmt = select(Url).where(Url.owner_id == current_user.id)
    user_result = await db.execute(stmt)

    user_urls = user_result.scalars().all()

    return user_urls


@route.get("/{short_code}")
async def get_qrcode(
    short_code: str = Path(..., min_length=6, max_length=6),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Url).where(Url.short_code == short_code)
    url_result = await db.execute(stmt)
    url_exist = url_result.scalar_one_or_none()

    if not url_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Url Not Found"
        )

    qrcode = generate_qr_code(data=url_exist.long_url)

    return qrcode


@route.post("/", response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
async def post_url(
    url_request: UrlRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. check if the user has already shortened the url
    stmt = (
        select(Url)
        .where(Url.long_url == url_request.long_url)
        .where(Url.owner_id == current_user.id)
    )
    result = await db.execute(stmt)
    existing_url = result.scalar_one_or_none()

    if existing_url:
        return existing_url

    # 2. generate 6 digits random short code
    short_code = generate_unique_code()

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

    try:
        db.add(database_url)
        await db.commit()
        await db.refresh(database_url)
    except Exception as e:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There is error. {e}",
        )

    return database_url


@route.post("/bulk", status_code=status.HTTP_200_OK, response_model=List[UrlResponse])
async def post_bulk_url(
    url_bulk_request: UrlBulkRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    long_url = url_bulk_request.long_url

    if not long_url:
        return []

    # fetch all url in one run
    stmt = select(Url).where(
        Url.owner_id == current_user.id, Url.long_url.in_(long_url)
    )
    url_result = await db.execute(stmt)
    url_existing = url_result.scalars().all()

    existing_url_map = {url.long_url: url for url in url_existing}

    final_url_list = []
    new_url_list = []

    for url in url_existing:
        if url.long_url in existing_url_map:
            final_url_list.append(url)

        short_code = generate_unique_code()

        if not short_code:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate short code Try Again Later",
            )

        database_url = Url(
            owner_id=current_user.id,
            short_code=short_code,
            is_active=True,
            created_at=url_bulk_request.created_at,
            expires_at=url_bulk_request.find_expire_at,
            long_url=url.long_url,
        )

        new_url_list.append(database_url)

    if new_url_list:
        try:
            db.add_all(new_url_list)
            await db.commit()

            for url in new_url_list:
                await db.refresh(url)

            final_url_list.extend(new_url_list)
        except Exception as e:
            await db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"There is error. {e}",
            )

    return final_url_list


@route.put("/{short_code}", status_code=status.HTTP_200_OK)
async def update_url_by_short_code(
    url_update_request: UrlUpdateRedquest,
    short_code: str = Path(..., min_length=6, max_length=6),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    stmt = select(Url).where(
        Url.short_code == short_code, Url.owner_id == current_user.id
    )
    url_result = await db.execute(stmt)
    url_update = url_result.scalar_one_or_none()

    if not url_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
        )

    url_model = url_update_request.model_dump(exclude_unset=True)

    for key, value in url_model.items():
        setattr(url_update, key, value)

    try:
        await db.commit()
        await db.refresh(url_update)
    except Exception as e:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There is some error {e}",
        )

    return url_update


@route.delete("/{short_code}")
async def delete_url_by_short_code(
    short_code: str = Path(..., min_length=6, max_digits=6),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Url).where(
        Url.owner_id == current_user.id, Url.short_code == short_code
    )
    url_result = await db.execute(stmt)
    url_delete = url_result.scalar_one_or_none()

    if not url_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Url Not Found"
        )

    try:
        await db.delete(url_delete)
        await db.refresh(url_delete)
    except Exception as e:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There is error {e}",
        )

    return url_delete
