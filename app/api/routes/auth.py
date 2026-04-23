from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from app.db.session import get_db
from app.schemas.user import Token, UserCreate, UserResponse
from app.services.auth import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["Auth"])

db_dependency = Annotated[Session, Depends(get_db)]
oauth_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user: UserCreate, db: db_dependency):
    return register_user(db, user.email, user.password)


@router.post("/login", response_model=Token)
async def login(form: oauth_dependency, db: db_dependency):
    token = authenticate_user(form.username, form.password, db)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}
