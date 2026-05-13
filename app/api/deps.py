from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from starlette import status
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.exceptions import ForbiddenException, NotFoundException
from app.models import User, UserRole


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Returns the user based on token

    Decodes the user token and return the user.

    Args:
        token (str): Token from the user request.
        db (Session): Database session dependency.

    Returns:
        User: user object containing id, email, hashed_password, role.

    Raises:
        HTTPException: if the token cannot be verified or no user is found.
    """
    try:
        user = decode_access_token(token=token)
    except JWTError:
        raise ForbiddenException("Could not validate credentials")
    user = db.query(User).filter(User.id == user.get("id")).first()
    if not user:
        raise NotFoundException("User no longer exists")
    return user


def require_role(*roles: UserRole):
    """
    Factory that returns a dependency allowing only the specified roles.

    Args:
        roles (UserRole): User roles to be checked against

    Returns:
        role checker funcion to be executed

    Raises:
        HTTPException: Raised when the user doesnt have the requried roles

    Usage:
        Depends(require_role(UserRole.admin))
        Depends(require_role(UserRole.admin, UserRole.user))
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in roles]}",
            )
        return current_user

    return role_checker


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Check if the current user has the 'admin' role

    Args:
        current_user (User): User to check

    Returns:
        User: Returns the same user

    Raises:
        HTTPException: Raised when the user has no 'admin' role
    """

    if current_user.role != UserRole.admin:
        raise ForbiddenException("Admin access required")
    return current_user


def require_user(current_user: User = Depends(get_current_user)) -> User:
    """Check if the current user has the 'user' role

    Args:
        current_user (User): User to check

    Returns:
        User: Returns the same user

    Raises:
        HTTPException: Raised when the user has no 'user' role
    """
    if current_user.role != UserRole.user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role required",
        )
    return current_user
