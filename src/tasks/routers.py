from fastapi import APIRouter, status, Depends

from src.tasks.dependencies import get_task_service, valid_author_tasks
from src.tasks.models import Task
from src.tasks.schemas import CreateTask, ShowTask, UpdateTask
from src.tasks.services import TaskService
from src.users.dependencies import get_current_user
from src.users.models import User


task_router = APIRouter(tags=["Task"])


@task_router.get(
    "/tasks", status_code=status.HTTP_200_OK, response_model=list[ShowTask]
)
async def users_tasks(
    user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.get_all(user.id)


@task_router.post(
    "/tasks", status_code=status.HTTP_201_CREATED, response_model=ShowTask
)
async def create_task(
    task_data: CreateTask,
    user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.create(task_data, user.id)


@task_router.patch(
    "/task/{task_id}", status_code=status.HTTP_200_OK, response_model=ShowTask
)
async def edit_task(
    task_data: UpdateTask,
    task: Task = Depends(valid_author_tasks),
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.update(task.id, task_data)


@task_router.delete(
    "/task/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    task: Task = Depends(valid_author_tasks),
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.remove(task.id)
