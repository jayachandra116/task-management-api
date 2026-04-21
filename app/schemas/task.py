from typing import Optional

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    title: str = Field(min_length=3)
    description: Optional[str] = Field(min_length=3, max_length=100)
    complete: bool = False


class TaskCreate(TaskBase):
    """Schema for creating a new task.(Request body)"""

    owner_id: int


class Task(TaskBase):
    """Schema for reading a task.(Response body)"""

    id: int
    owner_id: int
