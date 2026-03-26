import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.models import User, UserRole
from app.security import hash_password, create_access_token
import os

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client"""
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hash_password("TestPassword123"),
        role=UserRole.USER,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin(db):
    """Create test admin user"""
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password=hash_password("AdminPassword123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def user_token(test_user):
    """Create JWT token for test user"""
    return create_access_token(
        data={"sub": test_user.id, "role": test_user.role.value}
    )


@pytest.fixture
def admin_token(test_admin):
    """Create JWT token for test admin"""
    return create_access_token(
        data={"sub": test_admin.id, "role": test_admin.role.value}
    )
