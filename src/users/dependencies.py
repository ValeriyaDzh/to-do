from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from src.users.services import UserService


async def get_user_service(session: AsyncSession = Depends(get_async_session)):
    return UserService(session=session)
