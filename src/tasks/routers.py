from uuid import UUID

from fastapi import APIRouter, status, Depends

from src.tasks.dependencies import get_task_service, valid_author_tasks, valid_task_id
from src.exceptions import PermissionDeniedException, NotFoundException
from src.tasks.models import Task
from src.tasks.schemas import CreateTask, ShowTask, UpdateTask, Permission
from src.tasks.services import TaskService
from src.users.dependencies import get_current_user, get_user_service
from src.users.models import User
from src.users.services import UserService


task_router = APIRouter(tags=["Task"])


@task_router.get(
    "/tasks", status_code=status.HTTP_200_OK, response_model=list[ShowTask]
)
async def users_tasks(
    user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    user_tasks = await task_service.get_all(user.id)
    permissions_tasks = await task_service.get_all_read(user.id)
    all_tasks = {task.id: task for task in user_tasks + permissions_tasks}.values()

    return all_tasks


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
    user: User = Depends(get_current_user),
    task: Task = Depends(valid_task_id),
    task_service: TaskService = Depends(get_task_service),
):
    if task.author_id == user.id or task_service.permission.get(
        task.id, user.id, "edit"
    ):
        return await task_service.update(task.id, task_data)
    else:
        raise PermissionDeniedException


@task_router.delete(
    "/task/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    task: Task = Depends(valid_author_tasks),
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.remove(task.id)


@task_router.post("/task/{task_id}/permissions")
async def add_task_permission(
    permission: Permission,
    task=Depends(valid_author_tasks),
    task_service: TaskService = Depends(get_task_service),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_by_id(permission.user_id)
    if user:
        await task_service.permission.add(
            task.id, permission.user_id, permission.permission
        )
        return {
            "message": f"Add {permission.permission} permission to user {permission.user_id} for task {task.id}."
        }
    else:
        raise NotFoundException(f"User with id: {permission.user_id} does not exist")


@task_router.delete("/task/{task_id}/permissions")
async def delete_task_permission(
    permission: Permission,
    task=Depends(valid_author_tasks),
    task_service: TaskService = Depends(get_task_service),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_by_id(permission.user_id)
    if user:
        await task_service.permission.delete(
            task.id, permission.user_id, permission.permission
        )
        return {
            "message": f"Delete {permission.permission} permission to user {permission.user_id} for task {task.id}."
        }
    else:
        raise NotFoundException(f"User with id: {permission.user_id} does not exist")
