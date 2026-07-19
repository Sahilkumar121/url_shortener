from fastapi import APIRouter, HTTPException, Depends, status, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.users import User

from typing import List
from app.schemas.user import UserResponse, UserUpdateRequest

route = APIRouter(prefix="/admin", tags=["ADMIN"])

not_permitted = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Yor Are Not Permited"
)

user_not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
)


@route.get("/user", status_code=status.HTTP_200_OK, response_model=List[UserResponse])
async def get_all_user(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):

    if not current_user.is_admin:
        raise not_permitted

    stmt = select(User)
    result = await db.execute(stmt)

    users = result.scalars().all()

    return users


@route.get(
    "/user/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def get_user_by_id(
    user_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if not current_user.is_admin:
        raise not_permitted

    stmt = select(User).where(User.id == user_id)
    user_result = await db.execute(stmt)
    user = user_result.scalar_one_or_none()

    if not user:
        raise user_not_found

    return user


@route.put(
    "/user/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse
)
async def update_user(
    user_request: UserUpdateRequest,
    user_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if not current_user.is_admin:
        raise not_permitted

    stmt = select(User).where(User.id == user_id)
    user_result = await db.execute(stmt)
    user = user_result.scalar_one_or_none()

    if not user:
        raise user_not_found
    update_model = user_request.model_dump(exclude_unset=True)

    for key, value in update_model.items():
        setattr(user, key, value)

    try:
        await db.commit()
        await db.refresh(user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There is some error {e}",
        )

    return user


@route.delete("/user/{user_id}")
async def delete_user(
    user_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise not_permitted

    stmt = select(User).where(User.id == user_id)
    user_result = await db.execute(stmt)
    user = user_result.scalar_one_or_none()

    if not user:
        raise user_not_found

    try:
        await db.delete(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There is error {e}",
        )

    return user
