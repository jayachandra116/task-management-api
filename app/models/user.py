import enum

from sqlalchemy import Column, Integer, String,Enum
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)

    tasks = relationship("Task", back_populates="owner")
