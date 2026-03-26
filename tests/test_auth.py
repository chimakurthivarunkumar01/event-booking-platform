import pytest
from fastapi import status


def test_signup_success(client):
    """Test successful user signup"""
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["access_token"]
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["username"] == "newuser"


def test_signup_duplicate_email(client, test_user):
    """Test signup with duplicate email"""
    response = client.post(
        "/api/auth/signup",
        json={
            "email": test_user.email,
            "username": "different",
            "password": "SecurePass123"
        }
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_signup_weak_password(client):
    """Test signup with weak password"""
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "user@example.com",
            "username": "user",
            "password": "weak"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "TestPassword123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["access_token"]
    assert data["user"]["id"] == test_user.id


def test_login_invalid_password(client, test_user):
    """Test login with invalid password"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "WrongPassword123"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "Password123"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
