from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.exceptions import InvalidCredentialsException
from src.users.auth import JWTToken, Password
from src.users.dependencies import get_user_service, get_current_user
from src.users.schemas import CreateUser, ShowUser, Token
from src.users.services import UserService

user_router = APIRouter(tags=["User"])


@user_router.post(
    "/sign-up", status_code=status.HTTP_201_CREATED, response_model=ShowUser
)
async def create_user(
    user_data: CreateUser, user_service: UserService = Depends(get_user_service)
):
    return await user_service.create(user_data)


@user_router.post("/sign-in", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_by_login(form_data.username)

    if user and Password.verify(form_data.password, user.hashed_password):
        access_token = JWTToken.create_access_token({"sub": user.login})

        return Token(access_token=access_token, token_type="bearer")

    else:
        raise InvalidCredentialsException("Incorrect login or password")


@user_router.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user=Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.remove(user.id)
