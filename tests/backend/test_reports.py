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


async def get_token(client, email="reporttest@test.com"):
    reg = await client.post("/api/v1/auth/register", json={
        "email": email, "password": "testpass123", "full_name": "Report User",
    })
    if reg.status_code == 409:
        login = await client.post("/api/v1/auth/login", json={
            "email": email, "password": "testpass123"
        })
        return login.json()["access_token"]
    return reg.json()["access_token"]


@pytest.mark.asyncio
async def test_generate_report(client):
    token = await get_token(client, "rep1@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post("/api/v1/reports", headers=headers,
                                 json={"report_type": "pricing_summary", "product_id": "prod-001"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["type"] == "pricing_summary"
    assert "content" in data
    assert data["status"] in ("completed", "fallback")


@pytest.mark.asyncio
async def test_get_report(client):
    token = await get_token(client, "rep2@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    create = await client.post("/api/v1/reports", headers=headers,
                               json={"report_type": "competitor_analysis"})
    report_id = create.json()["id"]
    response = await client.get(f"/api/v1/reports/{report_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == report_id


@pytest.mark.asyncio
async def test_list_reports(client):
    token = await get_token(client, "rep3@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    await client.post("/api/v1/reports", headers=headers,
                      json={"report_type": "market_trend"})
    response = await client.get("/api/v1/reports", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_report_not_found(client):
    token = await get_token(client, "rep4@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/reports/nonexistent-id", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_report_unauthorized(client):
    response = await client.post("/api/v1/reports",
                                 json={"report_type": "pricing_summary"})
    assert response.status_code == 401