from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify the password and hashed password

    Args:
        plain_password (str): Plain password to check
        hashed_password (str): Hased password to check against

    Returns:
        bool: Returns True If the plain password matched the hash, else False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Returns the hash for the plain password

    Args:
        password (str): Plain password to hash

    Returns:
        Hash for the plain password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new access token

    Args:
        data (dict): Data to sign
        expires_delta (timedelta): Optional, Expiration for the access token

    Returns:
        str: Access token created from the data
    """
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Verify the token

    Args:
        token (str): Token to be verified

    Returns:
        dict: Dict containing email and id of the user

    Raises:
        JWTError: Raised when the email or user id not present in the token
    """
    settings = get_settings()
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    user_email: str = payload.get("sub")
    user_id: int = payload.get("id")
    if user_email is None or user_id is None:
        raise JWTError("Email/Id missing from token")
    return {"email": user_email, "id": user_id}
