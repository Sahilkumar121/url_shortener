from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import urls, auth, admin


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # start up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    # shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def home_page():
    return {"message": "URL Shortener "}


app.include_router(urls.route)
app.include_router(auth.route)
app.include_router(admin.route)
