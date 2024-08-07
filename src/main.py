from fastapi import FastAPI

from src.config import settings
from src.users.routers import users_router

settings.log.configure_logging()

app = FastAPI(title="ToDo")

app.include_router(users_router)
