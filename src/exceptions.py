from fastapi import HTTPException, status


class DatabaseException(HTTPException):

    def __init__(self, detail="Server error...Please try again later") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )
