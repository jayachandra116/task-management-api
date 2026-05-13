from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.exceptions import NotFoundException
from app.models import User, UserRole, Task
from app.schemas.filters import TaskFilterParams
from app.schemas.task import TaskCreate, TaskUpdate
from app.utils.db import db_transaction
from app.utils.filters import apply_task_filters
from app.utils.pagination import paginate
import logging

logger = logging.getLogger(__name__)
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(deps.get_current_user)]


def get_task_or_404(task_id: int, db: db_dependency) -> Task:
    """Returns the task with an id or return the HTTPException

    Args:
        task_id (int): Task id to get
        db (Session): Database session to use

    Returns:
        Task: Task to get

    Raises:
        NotFoundException: Raised when the task with id is not found
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise NotFoundException("Task not found")
    return task


def check_task_owership(task: Task, current_user: User) -> None:
    """Check if the current user is not admin and owns the given task

    Args:
        task (Task): Task to check
        current_user (User): User to check against

    Raises:
        NotFoundException: Raised when the current user doesnt own the task and the current user has no admin role

    """
    if current_user.role != UserRole.admin and task.owner_id != current_user.id:
        raise NotFoundException("Task")


def create_new_task(
    db: db_dependency, current_user: user_dependency, payload: TaskCreate
) -> Task:
    """Create a new task

    Args:
        db (Session): Database session to use
        current_user (User): Current logged in user
        payload (TaskCreate): New task details

    Returns:
        Task: Newly created task
    """
    new_task = Task(
        title=payload.title,
        description=payload.description,
        complete=False,
        owner_id=current_user.id,
    )

    with db_transaction(db):
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

    logger.info(f"Task created: '{new_task.title}' by user {current_user.email}")
    return new_task


def get_current_user_tasks(
    db: db_dependency,
    current_user: user_dependency,
    filters: TaskFilterParams,
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Items per page"),
) -> dict:
    """Get the tasks of the currently logged in user

    Args:
        db (Session): Database session to use
        current_user (User): Currently logged in user
        filters (TaskFilterParams): Task filters
        page (int, optional): Page number. Defaults to 1.
        size (int, optional): Items pre page. Defaults to 10.

    Returns:
        dict: Paginated task response
    """
    query = db.query(Task)
    if current_user.role != UserRole.admin:
        query = query.filter(Task.owner_id == current_user.id)
    query = apply_task_filters(query=query, filters=filters)
    return paginate(query, page, size)


def get_task_by_id(
    task_id: int, db: db_dependency, current_user: user_dependency
) -> Task:
    """Get the task by it's id

    Args:
        task_id (int): Task id
        db (Session): Database session to use
        current_user (User): Currently logged in user

    Returns:
        Task: Task to return
    """
    task = get_task_or_404(task_id, db)
    check_task_owership(task, current_user)
    return task


def update_task_by_id(
    task_id: int, payload: TaskUpdate, db: db_dependency, current_user: user_dependency
) -> Task:
    """Update task details by it's Id

    Args:
        task_id (int): Task id
        payload (TaskUpdate): Task data to update
        db (Session): Database session to use
        current_user (User): Currently loggedin user

    Returns:
        Task: updated Task
    """
    task = get_task_or_404(task_id, db)
    check_task_owership(task, current_user)
    with db_transaction(db):
        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(task, field, value)
        db.commit()
        db.refresh(task)
    logger.info(f"Task updated: '{task.title}' by user {current_user.email}")
    return task


def delete_task_by_id(
    task_id: int, db: db_dependency, current_user: user_dependency
) -> None:
    """Delete a task by id

    Args:
        task_id (int): Task id to delete
        db (Session): Database session to use
        current_user (User): Currently loggedin user
    """
    task = get_task_or_404(task_id, db)
    check_task_owership(task, current_user)
    with db_transaction(db):
        db.delete(task)
        db.commit()

    logger.info(f"Task deleted: '{task.title}' by user {current_user.email}")
