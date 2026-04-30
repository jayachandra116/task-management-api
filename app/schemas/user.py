from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserCreate(BaseModel):
    """Request: register a new user."""

    email: EmailStr
    password: str = Field(min_length=8)


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

    current_password: str
    new_password: str = Field(min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str
