from fastapi import HTTPException, status


class UserAlreadyExists(HTTPException):

    def __init__(self, detail="User already exist") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
