from fastapi import FastAPI

from src.config import settings

settings.log.configure_logging()

app = FastAPI(title="ToDo")
