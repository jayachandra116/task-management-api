import os
import pytest

from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models import User, UserRole
from app.core.security import get_password_hash

load_dotenv(".env.test")

# use a separate test database
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def regular_user(db):
    user = User(
        email="user@test.com",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.user,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db):
    user = User(
        email="admin@test.com",
        hashed_password=get_password_hash("adminpass123"),
        role=UserRole.admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def user_token(client, regular_user):
    response = client.post(
        "/auth/login",
        data={"username": "user@test.com", "password": "testpass123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, admin_user):
    response = client.post(
        "/auth/login",
        data={"username": "admin@test.com", "password": "adminpass123"},
    )
    return response.json()["access_token"]
