from pydantic import BaseModel, Field
from typing import Optional


class TaskFilterParams(BaseModel):
    """
    All filter fields are optional
    Only fields that are provided are applied to the query
    """

    complete: Optional[bool] = Field(
        default=None,
        description="Filter by completion status. true=completed, false=pending",
    )
    search: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Search in task title and description",
    )
