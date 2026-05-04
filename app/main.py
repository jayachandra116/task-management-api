from fastapi import FastAPI
from app.api.v1.router import router as v1_router


app = FastAPI(
    title="Task Management API",
    description="Task Management API with versioning",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(v1_router)


# Root
@app.get("/")
def root():
    return {
        "message": "Task management API",
        "versions": {"v1": "/app/v1"},
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
