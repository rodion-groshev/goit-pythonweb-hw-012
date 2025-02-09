import pytest
from unittest.mock import Mock
from sqlalchemy import select

from conftest import TestingSessionLocal
from src.database.models import User

user_data = {
    "username": "user_testing",
    "email": "testing@gmail.com",
    "password": "12345",
}


@pytest.mark.asyncio
async def test_register_user(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    response = client.post("api/auth/register", json=user_data)

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == "testing@gmail.com"
    assert data["username"] == "user_testing"
    assert "hashed_password" not in data



@pytest.mark.asyncio
async def test_register_existing_user(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    response = client.post(
        "api/auth/register",
        json=user_data,
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Користувач з таким email вже існує"


@pytest.mark.asyncio
async def test_login_user(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


@pytest.mark.asyncio
async def test_login_invalid_user(client):
    response = client.post(
        "api/auth/login", data={"username": "wronguser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Неправильний логін або пароль"


@pytest.mark.asyncio
async def test_confirm_email(client, get_token):
    response = client.get(f"api/auth/confirmed_email/{get_token}")
    assert response.status_code in [200, 400]
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_request_email_verification(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    response = client.post(
        "api/auth/request_email", json={"email": "testing@gmail.com"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Ваша електронна пошта вже підтверджена"


@pytest.mark.asyncio
async def test_forgot_password(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    response = client.post(
        "api/auth/forgot_password", json={"email": "testing@gmail.com"}
    )
    assert response.status_code == 200
    assert (
        response.json()["message"]
        == "Password reset email sent. Please check your inbox."
    )
