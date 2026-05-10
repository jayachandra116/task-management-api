from pydantic import BaseModel, EmailStr, Field
from app.models import UserRole
from app.schemas.pagination import PaginatedResponse


class UserCreate(BaseModel):
    """Request: register a new user."""

    email: EmailStr
    password: str = Field(
        min_length=8, description="Plain text password, Will be hashed before saving."
    )


class UserResponse(BaseModel):
    """Response: never expose password."""

    id: int
    email: str
    role: UserRole

    model_config = {
        "from_attributes": True,
    }


class UserRoleUpdate(BaseModel):
    """admin can update user role"""

    role: UserRole


class PasswordChange(BaseModel):
    """Request: Change user pwd"""

    current_password: str = Field(
        min_length=8, description="Current plain text password"
    )
    new_password: str = Field(
        min_length=8, description="New plain test password to use"
    )


class Token(BaseModel):
    access_token: str = Field(description="Access token")
    token_type: str = Field(description="Token type")


# paginated user response — used in admin list routes
UserPaginatedResponse = PaginatedResponse[UserResponse]
