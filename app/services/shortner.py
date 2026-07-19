from app.utils.short_code import generate_short_code

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


from app.dependencies import get_db
from app.models.urls import Url


async def generate_unique_code(db: AsyncSession = Depends(get_db)):
    for _ in range(5):
        potential_code = generate_short_code()
        code_stmt = select(Url).where(Url.short_code == potential_code)
        code_result = await db.execute(code_stmt)
        code_exists = code_result.scalar_one_or_none()

        if not code_exists:
            return potential_code

    return None
