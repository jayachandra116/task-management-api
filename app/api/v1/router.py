from fastapi import APIRouter
from app.api.v1.routers import auth, user, task

router = APIRouter(prefix="/app/v1")

router.include_router(auth.router)
router.include_router(user.router)
router.include_router(task.router)
