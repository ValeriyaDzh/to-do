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


class NotFoundException(HTTPException):
    def __init__(self, detail="Not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class PermissionDeniedException(HTTPException):
    def __init__(self, detail: str = "There are no permission for changes"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class AlreadyExistsException(HTTPException):
    def __init__(self, detail="Already exist"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
