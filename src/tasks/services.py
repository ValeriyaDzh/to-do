import logging
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import DatabaseException
from src.repositories import BaseRepository
from src.tasks.models import Task
from src.tasks.schemas import CreateTask, UpdateTask


logger = logging.getLogger(__name__)


class TaskService(BaseRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(model=Task, session=session)

    async def create(self, data: CreateTask, author: UUID) -> Task:

        data_dict = data.model_dump()
        data_dict["author_id"] = author
        created_task = await self.save(data_dict)

        return created_task

    async def get_by_id(self, id: UUID) -> Task | None:
        task = await self.get("id", id)

        return task

    async def get_all(self, author: UUID) -> list[Task]:
        tasks = await self.get("author_id", author, all=True)

        return tasks

    async def update(self, id: UUID, data: UpdateTask) -> Task:

        updated_task_dict = data.model_dump(exclude_none=True)
        try:
            data_update = (
                update(self.model)
                .where(self.model.id == id)
                .values(updated_task_dict)
                .returning(self.model)
            )

            updated_task = await self.session.execute(data_update)
            await self.session.commit()
            return updated_task.scalar_one()

        except Exception as e:
            logger.error(f"Error updating task:{id} in the database: {e}")
            raise DatabaseException

    async def remove(self, id: UUID):
        await self.delete(id)
