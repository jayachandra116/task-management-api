from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task import (
    create_new_task,
    delete_task_by_id,
    get_all_current_user_tasks,
    get_task_by_id,
    update_task_by_id,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
async def create_task(
    payload: TaskCreate, db: db_dependency, current_user: user_dependency
):
    return create_new_task(db, current_user, payload)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[TaskResponse])
async def get_all_tasks(db: db_dependency, current_user: user_dependency):
    return get_all_current_user_tasks(db, current_user)


@router.get("/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskResponse)
async def get_task(task_id: int, db: db_dependency, current_user: user_dependency):
    return get_task_by_id(task_id, db, current_user)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int, payload: TaskUpdate, db: db_dependency, current_user: user_dependency
):
    return update_task_by_id(task_id, payload, db, current_user)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: db_dependency, current_user: user_dependency):
    return delete_task_by_id(task_id, db, current_user)
