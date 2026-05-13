from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status
from typing import Annotated, Optional

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.filters import TaskFilterParams
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate, TaskPaginatedResponse
from app.services.task import (
    create_new_task,
    delete_task_by_id,
    get_current_user_tasks,
    get_task_by_id,
    update_task_by_id,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponse,
    summary="Create a new task",
    description="Create new task for the currently logged in user",
    tags=["Tasks"],
)
async def create_task(
    payload: TaskCreate, db: db_dependency, current_user: user_dependency
):
    return create_new_task(db, current_user, payload)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=TaskPaginatedResponse,
    summary="List the tasks",
    description="List all the tasks for the currently logged in users",
    tags=["Tasks"],
)
async def list_tasks(
    db: db_dependency,
    current_user: user_dependency,
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    complete: Optional[bool] = Query(
        default=None, description="Filter by completion status"
    ),
    search: Optional[str] = Query(
        default=None, min_length=1, description="Search in title and description"
    ),
):
    filters = TaskFilterParams(complete=complete, search=search)
    return get_current_user_tasks(db, current_user, filters, page, size)


@router.get(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=TaskResponse,
    summary="Get the task details",
    description="Get the task by its id of the currently logged in user",
    tags=["Tasks"],
)
async def get_task(task_id: int, db: db_dependency, current_user: user_dependency):
    return get_task_by_id(task_id, db, current_user)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    description="Update a task by its Id of the currently logged in user",
    tags=["Tasks"],
)
async def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: db_dependency,
    current_user: user_dependency,
):
    return update_task_by_id(task_id, payload, db, current_user)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Delete a task by its id of the currently logged in user",
    tags=["Tasks"],
)
async def delete_task(task_id: int, db: db_dependency, current_user: user_dependency):
    return delete_task_by_id(task_id, db, current_user)
