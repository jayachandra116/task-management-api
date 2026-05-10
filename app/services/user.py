from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.core.security import verify_password, get_password_hash

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


def get_user_by_id(user_id: int, db: db_dependency) -> User:
    """Get the user by Id

    Args:
        user_id (int): User's Id
        db (Session): Database session to use

    Raises:
        HTTPException: Raised when the user does nto exist

    Returns:
        User: User details
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def change_user_password(
    user: user_dependency, current_password: str, new_password: str, db: db_dependency
) -> None:
    """Change the current user password

    Args:
        user (User): User to change password
        current_password (str): Current password
        new_password (str): New Password to use
        db (Session): Database session to use

    Raises:
        HTTPException: Raised when the current password is incorrect
    """
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is incorrect"
        )
    user.hashed_password = get_password_hash(new_password)
    db.commit()
