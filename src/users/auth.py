from datetime import timedelta, datetime, UTC
from passlib.context import CryptContext
from jose import jwt

from src.config import settings


class Password:
    """
    Utility class for handling password operations.
    """

    PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hash(cls, password: str) -> str:
        return cls.PWD_CONTEXT.hash(password)

    @classmethod
    def verify(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.PWD_CONTEXT.verify(plain_password, hashed_password)


class JWTToken:
    """
    Utility class for handling JWT operations.
    """

    @staticmethod
    def _encode(data: dict, expires_delta: timedelta) -> str:

        to_encode = data.copy()
        to_encode.update({"exp": expires_delta})
        encoded = jwt.encode(
            claims=to_encode,
            key=settings.jwt.SECRET_KEY.get_secret_value(),
            algorithm=settings.jwt.ALGORITHM,
        )
        return encoded

    @classmethod
    def decode(cls, token: str | bytes) -> dict:

        decoded = jwt.decode(
            token=token,
            key=settings.jwt.SECRET_KEY.get_secret_value(),
            algorithms=settings.jwt.ALGORITHM,
        )
        return decoded

    @classmethod
    def create_access_token(
        cls, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        """
        Create a new access token.

        If not expiration time delta for the token provided,
        the default expiration from settings will be used.
        """
        payload = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        encoded_access_jwt = cls._encode(data=payload, expires_delta=expire)
        return encoded_access_jwt
