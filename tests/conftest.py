import pytest
from pytest_mock import mocker
import logging
from typing import AsyncGenerator

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient

from src.config import settings
from src.database import Base, get_async_session
from src.main import app
from src.tasks.models import Task
from src.users.auth import JWTToken
from src.users.models import User


logger = logging.getLogger(__name__)

test_engine = create_async_engine(
    settings.test_db.URL.get_secret_value(), poolclass=NullPool, echo=True
)

test_async_sessionmaker = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

Base.metadata.bied = test_engine


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_sessionmaker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session

TEST_USER = {
    "id": "1c9e02ef-f0b0-4336-beb5-aade2e704600",
    "login": "test",
    "hashed_password": "12345678",
}

TEST_TASK = {
    "id": "1c9e02ef-f0b0-4336-beb5-aade2e704547",
    "title": "test_task",
    "description": "the_best_of_the_best",
    "author_id": "1c9e02ef-f0b0-4336-beb5-aade2e704600",
}


@pytest.fixture(autouse=True, scope="session")
async def prepear_database():
    logger.debug("Preparing database...")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.debug("Database tables created successfully.")

    for model, data in ((User, TEST_USER), (Task, TEST_TASK)):
        async with test_async_sessionmaker() as session:
            try:
                logger.debug(f"Inserting test in {model}...")
                add_data = model(**data)
                session.add(add_data)
                await session.commit()
                logger.debug(f"Test {model} data inserted successfully.")
            except Exception as e:
                logger.error(f"Error inserting test: {e}")
                await session.rollback()
                logger.info("Rolled back transaction.")
    logger.debug("Database preparation complete.")

    yield

    logger.debug("Deleting database...")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.debug("Database tables delete successfully.")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


client = TestClient(app)


@pytest.fixture(scope="session")
async def api_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as api_client:
        yield api_client


@pytest.fixture
def mock_jwt_decode(mocker):
    return mocker.patch.object(JWTToken, "decode")
