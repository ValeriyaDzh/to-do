from uuid import UUID

from pydantic import BaseModel, field_validator

from src.exceptions import UnprocessableException


class TaskBase(BaseModel):
    title: str
    description: str | None = None

    @field_validator("title")
    def title_validator(value):
        if len(value) < 1:
            raise UnprocessableException("Title must contains at least one simbol")

        return value


class CreateTask(TaskBase):
    pass


class ShowTask(TaskBase):
    id: UUID
    is_done: bool

    class Config:
        orm_mode = True


class UpdateTask(TaskBase):
    title: str | None = None
    is_done: bool | None = None


class Permission(BaseModel):
    user_id: UUID
    permission: str

    @field_validator("permission")
    def permission_validator(value):
        if value not in ("read", "edit"):
            raise UnprocessableException("Valid permission: read or edit")

        return value

    class Config:
        orm_mode = True
