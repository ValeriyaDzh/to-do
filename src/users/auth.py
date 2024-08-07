from passlib.context import CryptContext


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
