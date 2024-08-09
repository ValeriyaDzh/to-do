import logging
from uuid import UUID

from sqlalchemy import update, select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import DatabaseException, AlreadyExistsException, NotFoundException
from src.repositories import BaseRepository
from src.tasks.models import Task, task_permissions
from src.tasks.schemas import CreateTask, UpdateTask


logger = logging.getLogger(__name__)


class TaskService(BaseRepository):

    def __init__(self, session: AsyncSession):
        self.permission = PermissionService(session=session)
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

    async def get_all_read(self, user_id: UUID) -> list[Task]:
        permissions = await self.permission.get_all(user_id)
        permissions_task = []
        for perm in permissions:
            task_id = perm["task_id"]
            found_task = await self.get_by_id(task_id)
            if found_task:
                permissions_task.append(found_task)

        return permissions_task

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


class PermissionService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, task_id: UUID, user_id: UUID, permission: str):

        try:
            result = await self.session.execute(
                select(task_permissions).where(
                    task_permissions.c.task_id == task_id,
                    task_permissions.c.user_id == user_id,
                    task_permissions.c.permission == permission,
                )
            )

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error get permission: {e}")
            raise DatabaseException

    async def get_all(self, user_id: UUID):

        try:
            result = await self.session.execute(
                select(task_permissions).where(task_permissions.c.user_id == user_id)
            )

            return result.mappings().all()

        except Exception as e:
            logger.error(f"Error get all permission from user id: {e}")
            raise DatabaseException

    async def add(self, task_id: UUID, user_id: UUID, permission: str):
        existing_permission = await self.get(task_id, user_id, permission)

        if existing_permission:
            raise AlreadyExistsException(f"This permission for user already exists.")

        try:
            edded_permission = await self.session.execute(
                insert(task_permissions).values(
                    task_id=task_id, user_id=user_id, permission=permission
                )
            )
            await self.session.commit()
            logger.info(
                f"Granted permission {permission} to user {user_id} for task {task_id}."
            )
            return edded_permission

        except Exception as e:
            logger.error(f"Error add permission: {e}")
            raise DatabaseException

    async def delete(self, task_id: UUID, user_id: UUID, permission: str):

        existing_permission = self.get(task_id, user_id, permission)

        if not existing_permission:
            raise NotFoundException("Permission for user not found")

        try:
            await self.session.execute(
                delete(task_permissions).where(
                    task_permissions.c.task_id == task_id,
                    task_permissions.c.user_id == user_id,
                    task_permissions.c.permission == permission,
                )
            )
            await self.session.commit()

        except Exception as e:
            logger.error(f"Error deleting permission: {e}")
            raise DatabaseException
