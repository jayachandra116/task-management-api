from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from db.session import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    complete = Column(Boolean, default=False)
