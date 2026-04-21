from fastapi import HTTPException
from jose import jwt
from app.core.security import SECRET_KEY, ALGORITHM


def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
