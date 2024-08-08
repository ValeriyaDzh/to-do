from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.exceptions import NotFoundException, AccessRightsException
from src.tasks.models import Task
from src.tasks.services import TaskService
from src.users.dependencies import get_current_user
from src.users.models import User


def get_task_service(session: AsyncSession = Depends(get_async_session)):
    return TaskService(session=session)


async def valid_task_id(
    task_id: UUID, task_service: TaskService = Depends(get_task_service)
) -> Task:
    task = await task_service.get_by_id(task_id)
    if not task:
        raise NotFoundException("Task not found")

    return task


async def valid_author_tasks(
    current_user: User = Depends(get_current_user),
    task: Task = Depends(valid_task_id),
) -> Task:
    if task.author_id != current_user.id:
        raise AccessRightsException

    return task
