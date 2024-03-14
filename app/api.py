# import app.models
from fastapi import FastAPI
from app.controllers import user, film, author, genre

app = FastAPI(title="Онлайн кинотератр", version="1.1.0")

@app.get("/", tags=["Root"])
async def read_root() -> dict:
    return {
        "message": "Welcome to my films application, use the /docs route to proceed"
    }

app.include_router(user.router)
app.include_router(author.router)
app.include_router(film.router)
app.include_router(genre.router)