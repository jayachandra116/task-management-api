from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.pagination import PaginatedResponse


class TaskCreate(BaseModel):
    """Request: Create a new task - owner_id will be from JWT"""

    title: str = Field(min_length=3, max_length=100, description="Title of the task")
    description: Optional[str] = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        return v.strip()


class TaskUpdate(BaseModel):
    """Request: Partial update - every field optional."""

    title: Optional[str] = Field(
        None, min_length=3, max_length=100, description="Title of the task"
    )
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

    id: int = Field("id of the task")
    title: str = Field(description="Title of the task")
    description: Optional[str] = Field(description="Description of the task")
    complete: bool = Field(description="Status of the task")
    owner_id: int = Field(description="Id of the owner of the task")

    model_config = {
        "from_attributes": True,
    }


# paginated task response — used as the return type in list routes
TaskPaginatedResponse = PaginatedResponse[TaskResponse]
