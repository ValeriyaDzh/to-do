from fastapi import HTTPException, status


class DatabaseException(HTTPException):

    def __init__(self, detail="Server error...Please try again later"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )


class UnprocessableException(HTTPException):

    def __init__(self, detail="Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


class InvalidCredentialsException(HTTPException):

    def __init__(self, detail="Could not validate credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
