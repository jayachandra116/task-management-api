from typing import Annotated

from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models import User, UserRole, Task
from app.schemas.filters import TaskFilterParams
from app.schemas.task import TaskCreate, TaskUpdate
from app.utils.filters import apply_task_filters
from app.utils.pagination import paginate

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(deps.get_current_user)]


def get_task_or_404(task_id: int, db: db_dependency):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def check_task_owership(task: Task, current_user: User):
    if current_user.role != UserRole.admin and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")


def create_new_task(
    db: db_dependency, current_user: user_dependency, payload: TaskCreate
):
    new_task = Task(
        title=payload.title,
        description=payload.description,
        complete=False,
        owner_id=current_user.id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_current_user_tasks(
    db: db_dependency,
    current_user: user_dependency,
    filters: TaskFilterParams,
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Items per page"),
):
    query = db.query(Task)
    if current_user.role != UserRole.admin:
        query = query.filter(Task.owner_id == current_user.id)
    query = apply_task_filters(query=query, filters=filters)
    return paginate(query, page, size)


def get_task_by_id(task_id: int, db: db_dependency, current_user: user_dependency):
    task = get_task_or_404(task_id, db)
    check_task_owership(task, current_user)
    return task


def update_task_by_id(
    task_id: int, payload: TaskUpdate, db: db_dependency, current_user: user_dependency
):
    task = get_task_or_404(task_id, db)
    check_task_owership(task, current_user)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task_by_id(task_id: int, db: db_dependency, current_user: user_dependency):
    task = get_task_or_404(task_id, db)
    check_task_owership(task, current_user)
    db.delete(task)
    db.commit()
