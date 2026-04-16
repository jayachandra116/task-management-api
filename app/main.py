from fastapi import FastAPI

app = FastAPI(title="Task Management API")


@app.get("/")
def read_root():
    return {"message": "API is running"}
