import models
from fastapi import FastAPI
from controllers.user import router

app = FastAPI()
app.include_router(router)
