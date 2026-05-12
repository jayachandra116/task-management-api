from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.exceptions import BadRequestException, NotFoundException
from app.models import User
from app.core.security import verify_password, get_password_hash
import logging

from app.utils.db import db_transaction

logger = logging.getLogger(__name__)
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


def get_user_by_id(user_id: int, db: db_dependency) -> User:
    """Get the user by Id

    Args:
        user_id (int): User's Id
        db (Session): Database session to use

    Raises:
        NotFoundException: Raised when the user does not exist

    Returns:
        User: User details
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User")
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
        BadRequestException: Raised when the current password is incorrect
    """
    if not verify_password(current_password, user.hashed_password):
        raise BadRequestException("Current password is incorrect")
    with db_transaction(db):
        user.hashed_password = get_password_hash(new_password)
        db.commit()
    logger.info(f"Password changed for user: {user.email}")
