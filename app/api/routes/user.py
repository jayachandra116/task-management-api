from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, PasswordChange
from app.services.user import change_user_password

router = APIRouter(prefix="/user", tags=["User"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
def get_user(user: user_dependency, db: db_dependency):
    return db.query(User).filter(User.id == user.id).first()


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: PasswordChange, db: db_dependency, current_user: user_dependency
):
    return change_user_password(
        current_user, payload.current_password, payload.new_password, db
    )
