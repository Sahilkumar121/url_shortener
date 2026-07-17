from fastapi import FastAPI

from app.routers import urls

app = FastAPI()


@app.get("/")
def home_page():
    return {
        "message": "URL Shortener "
    }


app.include_router(urls.route)
