from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token, get_password_hash
from app.db.session import get_db
from app.models import User
from app.models.user import UserRole


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
        HTTPException: If the email or password is incorrect

    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token({"sub": user.email, "id": user.id})
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
        HTTPException: Raised when the user's email already exists
    """
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(password)
    user = User(email=email, hashed_password=hashed, role=UserRole.user)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
