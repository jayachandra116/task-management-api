from math import ceil
from typing import TypeVar
from sqlalchemy.orm import Query

from app.schemas.pagination import PaginationMeta

T = TypeVar("T")


def paginate(query: Query, page: int, size: int) -> dict:
    """Takes a SQLAlchemy query, page and size.
    Return a dict with items and meta - ready to return from any route.
    """
    total_items = query.items()
    total_pages = ceil(total_items / size) if total_items > 0 else 1
    offset = (page - 1) * size

    items = query.offset(offset).limit(size).all()

    meta = PaginationMeta(
        page=page,
        size=size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )

    return {"items": items, "meta": meta}
