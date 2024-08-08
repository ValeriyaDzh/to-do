import pytest
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
    "id": "3918e5a0-04fc-484b-adc2-fd3c8a90b5nn",
    "login": "test",
    "password": "12345678",
}


@pytest.fixture(autouse=True, scope="session")
async def prepear_database():
    logger.debug("Preparing database...")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.debug("Database tables created successfully.")

    async with test_async_sessionmaker() as session:
        try:
            logger.debug(f"Inserting test in {User}...")
            add_data = User(**TEST_USER)
            session.add(add_data)
            await session.commit()
            logger.debug(f"Test {User} data inserted successfully.")
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
