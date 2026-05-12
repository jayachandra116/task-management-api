import logging

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.router import router as v1_router
from app.db.session import get_engine

logger = logging.getLogger(__name__)

description = "Task Management API with JWT auth, RBAC, pagination, filtering"

app = FastAPI(
    title="Task Management API",
    description=description,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(v1_router)


# -- Global exception handlers --
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exec: RequestValidationError
) -> JSONResponse:
    """Catches the Pydantic validation errors(422) and returns a clean, structured error response"""
    errors = []
    for error in exec.errors:
        errors.append(
            {
                "field": "->".join(str(e) for e in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )
    logger.warning(f"Validation error on {request.url}: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "Validation error", "errors": errors},
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Catches any unhandled SQLAlchemy errors at the top level.
    Prevents raw DB errors from leaking to the client
    """
    logger.error(f"Unhandled SQLAlchemyError on {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred"},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Catches any completely unhandled exception.
    Prevents stack traces leaking to client.
    """
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"},
    )


def check_migrations() -> None:
    try:
        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)
        with get_engine().connect() as conn:
            context = MigrationContext.configure(conn)
            currrent = context.get_current_revision()
            head = script.get_current_head()
            if currrent is None:
                logger.warning("No migration applied. Run: alembic upgrade head")
            elif currrent != head:
                logger.warning("Migrations behind. Run: alembic upgrade head")
            else:
                logger.info(f"Migrations up to date: {currrent}")
    except Exception as e:
        logger.error(f"Could not check migrations: {e}")


@app.on_event("startup")
def on_startup() -> None:
    check_migrations()


# Root
@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Task management API",
        "versions": {"v1": "/api/v1"},
        "docs": "/docs",
    }


@app.get("/health", tags=["Root"])
def health():
    return {"status": "healthy"}
