import uuid

from sqlalchemy import Column, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


task_permissions = Table(
    "task_permissions",
    Base.metadata,
    Column("user_login", String, ForeignKey("user.login", ondelete="CASCADE")),
    Column("task_id", UUID, ForeignKey("task.id", ondelete="CASCADE")),
    Column("permission", String, nullable=False),
)


class Task(Base):

    __tablename__ = "task"

    def __repr__(self) -> str:
        return f"Task: {self.id}"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        unique=True,
    )
    title = Column(String, nullable=False)
    description = Column(String)
    is_done = Column(Boolean, default=False)
    author_id = Column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    author = relationship("User", back_populates="tasks")
    permitted_users = relationship(
        "User", secondary=task_permissions, back_populates="task_permissions"
    )
