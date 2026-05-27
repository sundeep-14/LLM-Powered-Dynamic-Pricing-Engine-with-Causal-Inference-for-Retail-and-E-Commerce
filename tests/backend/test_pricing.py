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


async def get_token(client, email="pricingtest@test.com"):
    """Register or login and return token."""
    reg = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "testpass123",
        "full_name": "Pricing User",
    })
    if reg.status_code == 409:
        login = await client.post("/api/v1/auth/login", json={
            "email": email, "password": "testpass123"
        })
        return login.json()["access_token"]
    return reg.json()["access_token"]


@pytest.mark.asyncio
async def test_optimize_price(client):
    token = await get_token(client, "opt1@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/api/v1/pricing/prod-001/optimize",
        headers=headers,
        json={
            "base_price": 100.0,
            "cost_price": 60.0,
            "current_demand": 50.0,
            "price_elasticity": -1.5,
            "competitor_avg_price": 105.0,
            "stock": 100,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "optimal_price" in data
    assert "expected_profit" in data
    assert data["optimal_price"] > 60.0


@pytest.mark.asyncio
async def test_set_pricing_rule(client):
    token = await get_token(client, "opt2@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/api/v1/pricing/prod-001/rule",
        headers=headers,
        json={"strategy": "dynamic", "min_price": 80.0, "max_price": 150.0},
    )
    assert response.status_code == 201
    assert response.json()["strategy"] == "dynamic"


@pytest.mark.asyncio
async def test_get_pricing_rule(client):
    token = await get_token(client, "opt3@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    await client.post("/api/v1/pricing/prod-002/rule", headers=headers,
                      json={"strategy": "fixed"})
    response = await client.get("/api/v1/pricing/prod-002/rule", headers=headers)
    assert response.status_code == 200
    assert response.json()["strategy"] == "fixed"


@pytest.mark.asyncio
async def test_apply_price(client):
    token = await get_token(client, "opt4@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post("/api/v1/pricing/prod-001/apply",
                                 headers=headers, json={"price": 99.99})
    assert response.status_code == 200
    assert response.json()["applied_price"] == 99.99


@pytest.mark.asyncio
async def test_pricing_history(client):
    token = await get_token(client, "opt5@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    await client.post("/api/v1/pricing/prod-003/apply",
                      headers=headers, json={"price": 89.99})
    response = await client.get("/api/v1/pricing/prod-003/history", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_optimize_price_unauthorized(client):
    response = await client.post(
        "/api/v1/pricing/prod-001/optimize",
        json={"base_price": 100.0, "cost_price": 60.0, "current_demand": 50.0},
    )
    assert response.status_code == 401