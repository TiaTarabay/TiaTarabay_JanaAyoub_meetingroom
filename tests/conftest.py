import sys
import os

# Make project root importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from common.db.connection import Base, get_db
from common.auth.auth_backend import get_password_hash, create_access_token

from users_service.app import app as users_app
from rooms_service.app import app as rooms_app

from users_service.models import User
from rooms_service.models import Room

# ----------------------------
# TEST DATABASE SETUP
# ----------------------------

TEST_DB_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override FastAPI DB dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


users_app.dependency_overrides[get_db] = override_get_db
rooms_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create fresh test DB before tests run."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ----------------------------
# CLIENT FIXTURES
# ----------------------------

@pytest.fixture
def client_users():
    return TestClient(users_app)

@pytest.fixture
def client_rooms():
    return TestClient(rooms_app)


# ----------------------------
# ADMIN CREATION FIXTURE
# ----------------------------

@pytest.fixture(scope="session")
def create_admin():
    """Create admin once per test session."""
    db = TestingSessionLocal()
    admin = User(
        username="admin_test",
        email="admin@test.com",
        hashed_password=get_password_hash("adminpass"),
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.close()
    return admin


# ----------------------------
# ADMIN TOKEN FIXTURE
# ----------------------------

@pytest.fixture
def admin_token(create_admin):
    token = create_access_token({"id": create_admin.id, "role": "admin"})
    return token
