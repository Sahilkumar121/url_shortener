from typing import AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import setting
from app.database import SessionLocal
from app.models.users import User

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_schema), db: AsyncSession = Depends(get_db)
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate the credential",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, setting.SECRETE_KEY, algorithms=setting.ALGORITHM)

        user_id: str | None = payload.get("sub")
        if not user_id:
            raise credential_exception
    except JWTError:
        raise credential_exception

    stmt = select(User).where(User.email == int(user_id))
    user_result = await db.execute(stmt)
    user = user_result.scalar_one_or_none()

    if not user:
        raise credential_exception
    return user
