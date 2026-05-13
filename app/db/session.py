from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


@lru_cache()
def get_engine():
    settings = get_settings()
    return create_engine(settings.DATABASE_URL)


@lru_cache()
def get_sessionmaker():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db():
    """Returns the Database session"""
    db = get_sessionmaker()()
    try:
        yield db
    finally:
        db.close()
