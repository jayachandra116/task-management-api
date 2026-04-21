from fastapi import FastAPI
from app.api.routes import auth


app = FastAPI(title="Task Management API")

# Authentication
app.include_router(auth.router)

# Root
@app.get("/")
def read_root():
    return {"message": "API is running"}
