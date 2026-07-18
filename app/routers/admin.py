from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.users import User

route = APIRouter(prefix="/admin", tags=["ADMIN"])


@route.get("/user", status_code=status.HTTP_200_OK)
async def get_all_user(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not Authorized"
        )

    stmt = select(User)
    result = await db.execute(stmt)

    users = result.scalars().all()

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Users Not Found"
        )

    return users
