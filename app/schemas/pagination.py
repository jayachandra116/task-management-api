from pydantic import BaseModel, Field
from typing import TypeVar, Generic, List

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Request query parameters for pagination"""

    page: int = Field(default=1, ge=1, description="Page number, starts at 1")
    size: int = Field(default=10, ge=1, le=100, description="Items per page, max 100")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginationMeta(BaseModel):
    """Metadata returned with every paginated response."""

    page: int
    size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginaed response wrapping any list of items."""

    items: List[T]
    meta: PaginationMeta
