from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models import User
from app.schemas.user import (
    UserPaginatedResponse,
    UserResponse,
    PasswordChange,
    UserRoleUpdate,
)
from app.services.user import change_user_password
from app.services import admin

router = APIRouter(prefix="/users", tags=["Users"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    tags=["User"],
    summary="Get the current user",
    description="This returns the currently logged in user details",
)
def get_me(current_user: user_dependency):
    return current_user


@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["User Management"],
    summary="Change the user password",
    description="Change the current user's password",
)
async def change_current_user_password(
    payload: PasswordChange, db: db_dependency, current_user: user_dependency
):
    return change_user_password(
        current_user, payload.current_password, payload.new_password, db
    )


# For admin
@router.get(
    "/",
    response_model=UserPaginatedResponse,
    tags=["Admin"],
    summary="List all users",
    description="List all the users for admin users",
)
def list_users(
    db: db_dependency,
    user: User = Depends(require_admin),
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Items per page"),
):
    return admin.list_all_users(db, user, page, size)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    tags=["Admin"],
    summary="Get the user details",
    description="Get the user details to the admin users",
)
def get_user(
    user_id: int,
    db: db_dependency,
    user: User = Depends(require_admin),
):
    return admin.get_user(user_id, db, user)


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    tags=["Admin"],
    summary="Update the user",
    description="Update the given user by admin users",
)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: db_dependency,
    current_user: User = Depends(require_admin),
):
    return admin.update_user_role(user_id, payload, db, current_user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Admin"],
    summary="Delete a user",
    description="Delete the given user by admin users",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    admin.delete_user(user_id, db, current_user)
