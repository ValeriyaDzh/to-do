import uuid

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base
from src.tasks.models import task_permissions


class User(Base):

    __tablename__ = "user"

    id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        nullable=False,
        primary_key=True,
        unique=True,
    )
    login = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="author")
    task_permissions = relationship(
        "Task", secondary=task_permissions, back_populates="permitted_users"
    )
