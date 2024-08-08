from fastapi import FastAPI

from src.config import settings
from src.tasks.routers import task_router
from src.users.routers import user_router

settings.log.configure_logging()

app = FastAPI(title="ToDo")

routers = (user_router, task_router)

for router in routers:
    app.include_router(router, prefix="/api")
