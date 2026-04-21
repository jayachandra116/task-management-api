from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.schemas.user import Token, UserCreate, UserLogin
from app.db.session import get_db
from app.services.auth import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: db_dependency):
    return register_user(db, user.email, user.password)


@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: db_dependency):
    token = authenticate_user(user.email, user.password, db)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}
