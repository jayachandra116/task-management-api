from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.pagination import PaginatedResponse


class TaskCreate(BaseModel):
    """Request: Create a new task - owner_id will be from JWT"""

    title: str = Field(min_length=3, max_length=100)
    description: Optional[str] = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        return v.strip()


class TaskUpdate(BaseModel):
    """Request: Partial update - every field optional."""

    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    complete: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        if v is not None:
            return v.strip()
        return v


class TaskResponse(BaseModel):
    """Response: Full task details"""

    id: int
    title: str
    description: Optional[str]
    complete: bool
    owner_id: int

    model_config = {
        "from_attributes": True,
    }


# paginated task response — used as the return type in list routes
TaskPaginatedResponse = PaginatedResponse[TaskResponse]
