import pytest

from app.db.base import Base
import app.models

from alembic.config import Config
from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.session import get_db
from app.main import app
from app.models import User, UserRole


# Force Pydantic to load the .env.test file
# We clear the lru_cache to ensure we aren't using dev settings
get_settings.cache_clear()
test_settings = get_settings(".env.test")

if test_settings.POSTGRES_PORT != 5433:
    raise ValueError(
        f"Safety check failed: DATABASE_URL must use port 5433 for tests. Found: {test_settings.POSTGRES_PORT}"
    )
engine = create_engine(test_settings.DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def override_settings():
    """
    Overrides the get_settings dependency globally for all tests.
    """
    app.dependency_overrides[get_settings] = lambda: test_settings
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Initializes the schema once per test session."""
    alembic_cfg = Config("alembic.ini")
    url = str(test_settings.DATABASE_URL)
    print(f"\nDEBUG: Alembic connecting to: {url}")
    alembic_cfg.set_main_option("sqlalchemy.url", str(test_settings.DATABASE_URL))

    # Manually drop and create to ensure the DB matches your models exactly
    with engine.begin() as conn:
        Base.metadata.drop_all(bind=conn)
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))

    print(f"\n[TEST SETUP] Running migrations on: {test_settings.DATABASE_URL}")
    command.upgrade(alembic_cfg, "head")
    yield


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

    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    del app.dependency_overrides[get_db]


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
