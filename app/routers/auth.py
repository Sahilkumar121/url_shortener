from sqlalchemy import select

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.dependencies import get_db
from app.models.users import User
from app.schemas.user import UserRequest, UserResponse

from app.core.security import get_hash_password

route = APIRouter(prefix="/auth", tags=["users"])


@route.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user_request: UserRequest, db: AsyncSession = Depends(get_db)):
    email_stmt = select(User).where(User.email == user_request.email)
    email_result = await db.execute(email_stmt)
    email_exist = email_result.scalar_one_or_none()

    if email_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User Already Exists"
        )

    user_data = user_request.model_dump()

    hashed_password = get_hash_password(user_data["password"])
    
    user_data["password"] = hashed_password
    user_register = User(**user_data)

    db.add(user_register)
    await db.commit()
    await db.refresh(user_register)

    return user_register
