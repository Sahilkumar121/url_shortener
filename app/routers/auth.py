from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.security import get_hash_password, verify_hash_password, create_access_token
from app.dependencies import get_db
from app.models.users import User
from app.schemas.user import UserRequest, UserResponse

route = APIRouter(prefix="/auth", tags=["Authentication"])


@route.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user_request: UserRequest, db: AsyncSession = Depends(get_db)):
    email_stmt = select(User).where(User.email == user_request.email, User.email == user_request.email)
    email_result = await db.execute(email_stmt)
    email_exist = email_result.scalar_one_or_none()

    if email_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User Already Exists"
        )

    user_data = user_request.model_dump()

    hashed_password = get_hash_password(user_data["password"])

    del user_data["password"]
    user_data["hashed_password"] = hashed_password
    user_register = User(**user_data)

    db.add(user_register)
    await db.commit()
    await db.refresh(user_register)

    return user_register


@route.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == form_data.username)

    user_result = await db.execute(stmt)
    user_exist: User | None = user_result.scalars().first()

    if not user_exist or not verify_hash_password(form_data.password, user_exist.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Failed")

    return {
        "access_token": create_access_token(data={'sub': user_exist.id}),
        "token_type": "bearer"
    }
