import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_shorten_url(client: AsyncClient):
    response = await client.post("/shorten", json={"url": "https://example.com/some/long/path"})
    assert response.status_code == 201
    data = response.json()
    assert "code" in data
    assert "short_url" in data
    assert data["original_url"] == "https://example.com/some/long/path"
    assert len(data["code"]) == 7


@pytest.mark.asyncio
async def test_shorten_with_custom_code(client: AsyncClient):
    response = await client.post(
        "/shorten", json={"url": "https://example.com/custom", "custom_code": "mycode1"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "mycode1"


@pytest.mark.asyncio
async def test_shorten_duplicate_custom_code(client: AsyncClient):
    await client.post(
        "/shorten", json={"url": "https://example.com/first", "custom_code": "dupcode"}
    )
    response = await client.post(
        "/shorten", json={"url": "https://example.com/second", "custom_code": "dupcode"}
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_redirect(client: AsyncClient):
    res = await client.post("/shorten", json={"url": "https://redirect-target.com"})
    code = res.json()["code"]

    response = await client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://redirect-target.com"


@pytest.mark.asyncio
async def test_redirect_not_found(client: AsyncClient):
    response = await client.get("/doesnotexist999", follow_redirects=False)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_stats(client: AsyncClient):
    res = await client.post("/shorten", json={"url": "https://stats-test.com"})
    code = res.json()["code"]

    # Hit it twice
    await client.get(f"/{code}", follow_redirects=False)
    await client.get(f"/{code}", follow_redirects=False)

    stats = await client.get(f"/stats/{code}")
    assert stats.status_code == 200
    data = stats.json()
    assert data["code"] == code
    assert data["hit_count"] == 2


@pytest.mark.asyncio
async def test_stats_not_found(client: AsyncClient):
    response = await client.get("/stats/nonexistentcode")
    assert response.status_code == 404
