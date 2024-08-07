import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import BaseRepository
from src.users.auth import Password
from src.users.exceptions import UserAlreadyExists
from src.users.models import User
from src.users.schemas import CreateUser


logger = logging.getLogger(__name__)


class UserService(BaseRepository):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=User, session=session)

    async def create(self, data: CreateUser) -> User:

        if await self.get_by_login(data.login):
            logger.error(f"User with {data.login} already exist")
            raise UserAlreadyExists

        data_dict = data.model_dump()
        password = data_dict.pop("password")
        data_dict["hashed_password"] = Password.hash(password)
        logger.debug(f"Prepeared data for: {data_dict}")

        created_user = await self.save(data_dict)
        return created_user

    async def get_by_login(self, user_login: str) -> User | None:
        user = await self.get("login", user_login)
        return user

    async def remove(self, user_id: UUID):
        await self.delete(user_id)
