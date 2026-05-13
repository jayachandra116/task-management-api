from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError, DataError, DatabaseError
import logging

from app.exceptions import DatabaseException, ConflictException

logger = logging.getLogger(__name__)


@contextmanager
def db_transaction(db: Session) -> Generator:
    """Context manager that wraps a DB operation with:
        - automatic rollback on any exception
        - clean HTTP exception instead of raw SQLAlchemy errors
        - structured logging of all DB errors

    Usage:
        with db_transaction(db):
            db.add(user)
            db.commit()
            db.refresh(user)
    """
    try:
        yield db
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError: {e.orig}")

        # unique constraint — e.g. duplicate email
        if (
            "unique constraint" in str(e.orig).lower()
            or "duplicate key" in str(e.orig).lower()
        ):
            raise ConflictException("A record with this value already exists.")

        # foreign key violation
        if "foreign key" in str(e.orig).lower():
            raise DatabaseException("Related resource does not exist")

        raise DatabaseException("Data integrity error occurred.")
    except OperationalError as e:
        db.rollback()
        logger.error(f"OperationalError: {e.orig}")
        raise DatabaseException("Database connection error occurred")
    except DataError as e:
        db.rollback()
        logger.error(f"DataError: {e.orig}")
        raise DatabaseException("Invalid data format provided")
    except DatabaseError as e:
        db.rollback()
        logger.error(f"DatabaseError: {e.orig}")
        raise DatabaseException("An unexpected database error occurred")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during DB transaction: {e}")
        raise DatabaseException("An unexpected error occurred")
