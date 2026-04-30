from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models import User
from app.schemas.user import UserResponse, PasswordChange, UserRoleUpdate
from app.services.user import change_user_password
from app.services import admin

router = APIRouter(prefix="/user", tags=["User"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
def get_me(current_user: user_dependency):
    return current_user


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_current_user_password(
    payload: PasswordChange, db: db_dependency, current_user: user_dependency
):
    return change_user_password(
        current_user, payload.current_password, payload.new_password, db
    )


# For admin
@router.get("/", response_model=List[UserResponse])
def list_users(db: db_dependency, user: User = Depends(require_admin)):
    return admin.list_all_users(db, user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: db_dependency,
    user: User = Depends(require_admin),
):
    return admin.get_user(user_id, db, user)


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: db_dependency,
    current_user: User = Depends(require_admin),
):
    return admin.update_user_role(user_id, payload, db, current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    admin.delete_user(user_id, db, current_user)
