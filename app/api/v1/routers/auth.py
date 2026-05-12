from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from app.db.session import get_db
from app.exceptions import ForbiddenException
from app.schemas.user import Token, UserCreate, UserResponse
from app.services.auth import authenticate_user, register_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])

db_dependency = Annotated[Session, Depends(get_db)]
oauth_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Creates a new user",
    tags=["Auth"],
    description="""
        Registers a new user account with email must be unique
    """,
)
async def register(user: UserCreate, db: db_dependency):
    return register_user(db, user.email, user.password)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Login the registered user and returns the token",
    tags=["Auth"],
)
async def login(form: oauth_dependency, db: db_dependency):
    token = authenticate_user(form.username, form.password, db)
    if not token:
        raise ForbiddenException(detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}
