from fastapi import HTTPException, status


class BadRequestException(HTTPException):
    """Raised when a request is invalid."""

    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnAuthorizedException(HTTPException):
    """Raised when a user is not authorized"""

    def __init__(self, detail: str = "Not authorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(HTTPException):
    """Raised when a user does not have access rights"""

    def __init__(
        self,
        detail: str = "Forbidden",
    ):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(HTTPException):
    """Raised when a requested resource does not exist"""

    def __init__(self, detail: str = "Resource does not exist"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictException(HTTPException):
    """Raised when a resource already exists"""

    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class DatabaseException(HTTPException):
    """Raised when a database operation fails unexpectedly"""

    def __init__(self, detail: str = "A database error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
