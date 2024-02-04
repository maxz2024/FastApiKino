import models
from fastapi import FastAPI
from controllers import user, film

app = FastAPI(title="Онлайн кинотератр", version="1.1.0")
app.include_router(user.router)
app.include_router(film.router)

