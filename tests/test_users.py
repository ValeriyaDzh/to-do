import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_signup(api_client: AsyncClient):
    user_data = {"login": "john_doe", "password": "12345678"}

    response = await api_client.post("/sign-up", json=user_data)
    assert response.status_code == 201

    data = response.json()
    for key, value in data.items():
        assert value == user_data[key]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user_data, status, detail",
    [
        (
            {
                "login": "john_doe",
                "password": "12345678",
            },
            409,
            "User with this login already exists",
        ),
        (
            {
                "login": "j",
                "password": "12345678",
            },
            422,
            "Login must be at least 4 characters long",
        ),
        (
            {
                "login": "johndoe",
                "password": "123",
            },
            422,
            "Password must be at least 8 characters long",
        ),
    ],
)
async def test_signup_exeptions(api_client: AsyncClient, user_data, status, detail):

    response = await api_client.post("/sign-up", json=user_data)
    assert response.status_code == status

    data = response.json()
    assert detail in data["detail"]


@pytest.mark.anyio
async def test_signin(api_client: AsyncClient):
    user_data = {"username": "john_doe", "password": "12345678"}

    response = await api_client.post("/sign-in", data=user_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user_data",
    [
        ({"username": "john_doe", "password": "1"}),
        ({"username": "johndoe", "password": "12345678"}),
    ],
)
async def test_signin_exeptions(api_client: AsyncClient, user_data):

    response = await api_client.post("/sign-in", data=user_data)
    assert response.status_code == 401

    data = response.json()
    assert "Incorrect login or password" in data["detail"]
