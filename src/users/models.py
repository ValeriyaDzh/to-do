import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


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
