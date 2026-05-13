from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.exceptions import BadRequestException, NotFoundException
from app.models import User
from app.schemas.user import UserRoleUpdate
from app.utils.db import db_transaction
from app.utils.pagination import paginate
import logging

logger = logging.getLogger(__name__)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


def list_all_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Items per page"),
) -> dict:
    """List all the users in the DB

    Args:
        db (Session): Database session
        page (int): Page number of the response to get
        size (int): Items per page

    Returns:
        dict: Paginated response
    """
    query = db.query(User)
    return paginate(query, page, size)


def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> User:
    """Get the user

    Args:
        user_id (int): User id to get
        db (Session): Database session to use

    Returns:
        User: User object

    Raises:
        NotFoundException: Raised when the user to retrieve is not found.
    """

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User")
    return user


def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),  # only admins can change roles
) -> User:
    """Returns the updated user

    Args:
        user_id (int): User id to update
        payload (UserRoleUpdate): Role details
        db (Session): Database session to use
        current_user (User): Current admin user

    Returns:
        User: Updated user object

    Raises:
        BadRequestException: Raised If the current admin user wants to change their own role
        NotFoundException: Raised if the user to update is not found
    """
    if current_user.id == user_id:
        raise BadRequestException("Admins cannot change their own role")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User")

    with db_transaction(db):
        user.role = payload.role
        db.commit()
        db.refresh(user)
    logger.info(f"Role updated for user {user.email} to {user.role}")
    return user


def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> None:
    """Delete a user from database

    Args:
        user_id (int): User id to delete
        db (Session): Database session to use
        current_user (User): Current logged in user

    Raises:
        BadRequestException: Raised when admins try to delete themselves
        NotFoundException: Raised when the use is not found
    """
    if current_user.id == user_id:
        raise BadRequestException("Admins cannot delete themselves")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User")

    with db_transaction(db):
        db.delete(user)
        db.commit()

    logger.info(f"User deleted: {user.email}")
