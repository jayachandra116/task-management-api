from fastapi import FastAPI
from app.api.routes import auth, task, user


app = FastAPI(title="Task Management API")

# Authentication
app.include_router(auth.router)

# Task
app.include_router(task.router)

# Users
app.include_router(user.router)


# Root
@app.get("/")
def read_root():
    return {"message": "API is running"}
