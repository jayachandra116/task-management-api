from app.models.user import User, UserRole  # import User first
from app.models.task import Task  # then Task

# explicitly export all so other modules can do:
# from app.models import User, Task, UserRole
__all__ = ["User", "UserRole", "Task"]
