from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    """Schema for a new user registration(Request body)"""

    password: str


class User(UserBase):
    """Schema for reading a user(Response body)"""

    id: int
