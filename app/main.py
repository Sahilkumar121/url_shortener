from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.routers import urls, auth, admin
from app.core.rate_limiting import limiter

from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # start up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    # shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_handle(_request: Request, _ext: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too Many Requests"},
    )


app.add_middleware(SlowAPIMiddleware)


@app.get("/")
@limiter.exempt
def home_page(_request: Request):
    return {"message": "URL Shortener "}


app.include_router(urls.route)
app.include_router(auth.route)
app.include_router(admin.route)
