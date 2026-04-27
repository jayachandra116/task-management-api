from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Request: register a new user."""

    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    """Response: never expose password."""

    id: int
    email: str


class PasswordChange(BaseModel):
    """Request: Change user pwd"""

    current_password: str
    new_password: str = Field(min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str
