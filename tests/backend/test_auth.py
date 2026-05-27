import pytest
from httpx import AsyncClient, ASGITransport
from backend.api.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as c:
        yield c


@pytest.fixture
async def auth_headers(client):
    """Register a user and return auth headers."""
    response = await client.post("/api/v1/auth/register", json={
        "email": "testuser@test.com",
        "password": "testpass123",
        "full_name": "Test User",
    })
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "newuser@test.com",
        "password": "password123",
        "full_name": "New User",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {
        "email": "duplicate@test.com",
        "password": "password123",
        "full_name": "User",
    }
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/api/v1/auth/register", json={
        "email": "logintest@test.com",
        "password": "password123",
        "full_name": "Login User",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "logintest@test.com",
        "password": "password123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={
        "email": "wrongpass@test.com",
        "password": "correctpass",
        "full_name": "User",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "wrongpass@test.com",
        "password": "wrongpass",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile(client, auth_headers):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@test.com"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_protected_route_without_token(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "refreshtest@test.com",
        "password": "password123",
        "full_name": "Refresh User",
    })
    refresh_token = reg.json()["refresh_token"]
    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    assert "access_token" in response.json()