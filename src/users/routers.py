from fastapi import APIRouter, status, Depends

from src.users.dependencies import get_user_service
from src.users.schemas import CreateUser, ShowUser
from src.users.services import UserService

users_router = APIRouter(tags=["User"])


@users_router.post(
    "/sign-up", status_code=status.HTTP_201_CREATED, response_model=ShowUser
)
async def create_user(
    user_data: CreateUser, user_service: UserService = Depends(get_user_service)
):
    return await user_service.create(user_data)
