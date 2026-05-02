from sqlalchemy import or_
from sqlalchemy.orm import Query

from app.models import Task
from app.schemas.filters import TaskFilterParams


def apply_task_filters(query: Query, filters: TaskFilterParams) -> Query:
    """
    Applies only the filters that were provided.
    Unset fields are ignored - never filter on None values.
    """
    if filters.complete is not None:
        query = query.filter(Task.complete == filters.complete)

    if filters.search is not None:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(Task.title.ilike(search_term), Task.description.ilike(search_term))
        )

    return query
