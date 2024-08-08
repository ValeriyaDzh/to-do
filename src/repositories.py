import logging
from uuid import UUID
from typing import Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class BaseRepository:
    """
    Base repository providing generic database
    Create, Get, Delete operations.
    """

    def __init__(self, model, session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def save(self, playload: dict[str, Any]) -> Any:
        """
        Save a new entity in the database.

        :param payload: data for the new entity.
        :return: the saved entity.
        :raises DatabaseException: if a database error occurs.
        """
        try:
            entity = self.model(**playload)
            self.session.add(entity)
            await self.session.commit()
            return entity

        except Exception as e:
            logger.error(f"Error saving entity in database: {e}")

    async def get(self, key: str, value: str | bool, all: bool = False) -> Any:
        """
        Get entity from the database by a specified field.

        :param key: field name.
        :param value: field value.
        :param all: whether to retrieve all matching entities. Defaults to `False`
        :return: a list of entities if `all` is True, else a single entity or None.
        :raises DatabaseException: if a database error occurs.
        """
        try:
            result = await self.session.execute(
                select(self.model).where((getattr(self.model, key) == value))
            )
            if all:
                entities = result.scalars().all()
                logger.debug(f"Entities from {value}: {entities}")
                return entities

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error get entity from database: {e}")

    async def delete(self, entity_id: UUID) -> None:
        """
        Delete an entity from the database by id.

        :param entity_id: the id of the entity.
        :raises DatabaseException: if a database error occurs.
        """
        try:
            await self.session.execute(
                delete(self.model).where(self.model.id == entity_id)
            )
            await self.session.commit()

        except Exception as e:
            logger.error(f"Error deliting entity from database: {e}")
