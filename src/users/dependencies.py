import logging
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.exceptions import InvalidCredentialsException
from src.users.auth import JWTToken
from src.users.models import User
from src.users.services import UserService

logger = logging.getLogger(__name__)

ouath2_schema = OAuth2PasswordBearer(tokenUrl="api/sign-in")


async def get_user_service(session: AsyncSession = Depends(get_async_session)):
    return UserService(session=session)


async def get_current_user(
    token: str = Depends(ouath2_schema),
    user_service: UserService = Depends(get_user_service),
) -> User:
    try:
        playload = JWTToken.decode(token)
        login = playload.get("sub")
        if login is None:
            raise InvalidCredentialsException
    except JWTError as e:
        logger.error(f"Error decode JWT token: {e}")
        raise InvalidCredentialsException

    user = await user_service.get_by_login(login)
    if not user:
        raise InvalidCredentialsException

    return user
