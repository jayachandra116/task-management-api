import os
import pytest
from dotenv import load_dotenv

# Load the environment before importing app-specific modules
load_dotenv(".env.test", override=True)  # noqa: E402

from alembic.config import Config
from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import get_password_hash
from app.db.session import get_db
from app.main import app
from app.models import User, UserRole

# Global test engine setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL or "5433" not in DATABASE_URL:
    raise ValueError("DATABASE_URL in .env.test must point to port 5433")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Initializes the schema once per test session."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    yield
    # Optional: Base.metadata.drop_all(bind=engine)
    # Usually better to leave it for manual inspection if a run fails


@pytest.fixture
def db():
    """
    Creates a fresh database session for a test.
    Wraps the session in a transaction that rolls back after the test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db):
    """Overrides the get_db dependency to use the transactional test session."""

    def override_get_db():
        try:
            yield db
        finally:
            pass  # Session cleanup is handled by the db fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def regular_user(db):
    user = User(
        email="user@test.com",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.user,
    )
    db.add(user)
    # Use flush instead of commit to stay within the transaction
    db.flush()
    return user


@pytest.fixture
def admin_user(db):
    user = User(
        email="admin@test.com",
        hashed_password=get_password_hash("adminpass123"),
        role=UserRole.admin,
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def user_token(client, regular_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@test.com", "password": "testpass123"},
    )
    return response.json().get("access_token")


@pytest.fixture
def admin_token(client, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "adminpass123"},
    )
    return response.json().get("access_token")
