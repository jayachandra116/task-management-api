from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token, get_password_hash
from app.db.session import get_db
from app.exceptions import ConflictException, NotFoundException, UnAuthorizedException
from app.models import User
from app.models.user import UserRole
import logging

from app.utils.db import db_transaction

logger = logging.getLogger(__name__)

db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(email: str, password: str, db: db_dependency) -> str:
    """Returns the access token if the user email and password is verfied

    Args:
        email (str): Email of the user
        password (str): Password of the user
        db (Session): Database session to use

    Returns:
        str: User token

    Raises:
        NotFoundException: If the user with the email do not exist
        UnAuthorizedException: If the user's email or password do not match
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise NotFoundException("User does not exist")
    if not verify_password(password, user.hashed_password):
        raise UnAuthorizedException(detail="Incorrect email or password")
    token = create_access_token({"sub": user.email, "id": user.id})
    logger.info(f"User logged in: {user.email}")
    return token


def register_user(db: db_dependency, email: str, password: str) -> User:
    """Registers a new user

    Args:
        db (Session): Database session to use
        email (str): Email of the user
        password (str): Password of the user

    Returns:
        User: Newly created user

    Raises:
        ConflictException: Raised when the user's email already exists
    """
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        raise ConflictException(detail="Email already registered")
    hashed = get_password_hash(password)
    user = User(email=email, hashed_password=hashed, role=UserRole.user)
    with db_transaction(db):
        db.add(user)
        db.commit()
        db.refresh(user)

    logger.info(f"New user registered: {user.email} with role {user.role}")
    return user
