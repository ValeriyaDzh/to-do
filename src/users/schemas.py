from uuid import UUID

from pydantic import BaseModel, field_validator

from src.exceptions import UnprocessableException


class CreateUser(BaseModel):
    login: str
    password: str

    @field_validator("login")
    def login_validator(cls, value):
        if len(value) < 4:
            raise UnprocessableException("Login must be at least 4 characters long")
        return value

    @field_validator("password")
    def password_valodator(cls, value):
        if len(value) < 8:
            raise UnprocessableException("Password must be at least 8 characters long")

        return value


class ShowUser(BaseModel):
    login: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
