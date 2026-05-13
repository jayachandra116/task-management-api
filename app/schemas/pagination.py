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

    page: int = Field(description="Page number")
    size: int = Field(description="Size of the page")
    total_items: int = Field(description="Total number of items")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="If the response has a next page")
    has_previous: bool = Field(description="If the response has a previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginaed response wrapping any list of items."""

    items: List[T] = Field(description="List of items")
    meta: PaginationMeta = Field(description="Metadata about the response")
