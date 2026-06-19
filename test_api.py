"""
Integration tests for NexusAI API.
Uses pytest-asyncio and httpx AsyncClient against a test database.
"""

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.db.session import Base, get_db
from app.core.config import settings

# ── Test DB Setup ─────────────────────────────────────────────────────────────

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
async def create_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def registered_user(client: AsyncClient):
    """Register and return a user + tokens."""
    payload = {
        "email": f"test_{uuid.uuid4().hex[:8]}@nexusai.test",
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "password": "TestPass123",
        "full_name": "Test User",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.json()

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    return {"user": resp.json(), "tokens": tokens, "credentials": payload}


@pytest.fixture
def auth_headers(registered_user):
    token = registered_user["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── Health Tests ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["app"] == "NexusAI"
    assert data["status"] == "operational"


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


# ── Auth Tests ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "username": "newuser_test",
            "password": "StrongPass1",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newuser@test.com"
    assert data["role"] == "user"
    assert data["plan"] == "free"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, registered_user):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": registered_user["credentials"]["email"],
            "username": "differentuser",
            "password": "StrongPass1",
        },
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "weak@test.com", "username": "weakuser", "password": "weak"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, registered_user):
    resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["credentials"]["email"],
            "password": registered_user["credentials"]["password"],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, registered_user):
    resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["credentials"]["email"],
            "password": "WrongPassword1",
        },
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(client: AsyncClient, registered_user, auth_headers):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == registered_user["credentials"]["email"]


@pytest.mark.asyncio
async def test_me_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, registered_user):
    refresh = registered_user["tokens"]["refresh_token"]
    resp = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


# ── User Tests ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_profile(client: AsyncClient, auth_headers):
    resp = await client.get("/api/v1/users/me", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, auth_headers):
    resp = await client.patch(
        "/api/v1/users/me",
        json={"full_name": "Updated Name"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_get_stats(client: AsyncClient, auth_headers):
    resp = await client.get("/api/v1/users/me/stats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "tokens_used_this_month" in data
    assert "monthly_token_limit" in data
    assert data["plan"] == "free"


@pytest.mark.asyncio
async def test_create_api_key(client: AsyncClient, auth_headers):
    resp = await client.post(
        "/api/v1/users/me/api-keys",
        json={"name": "My Test Key"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "full_key" in data
    assert data["full_key"].startswith("nxs_sk_")
    assert data["name"] == "My Test Key"


# ── Admin Tests ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_access_denied_for_regular_user(
    client: AsyncClient, auth_headers
):
    resp = await client.get("/api/v1/admin/stats", headers=auth_headers)
    assert resp.status_code == 403


# ── Generation Tests (mocked) ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_generations_empty(client: AsyncClient, auth_headers):
    resp = await client.get("/api/v1/generate", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_generation_no_openai_key(
    client: AsyncClient, auth_headers, monkeypatch
):
    """
    Without a real OpenAI key the service raises an error.
    Test that we get a proper 500 (not a crash) in that case.
    """
    from app.services import ai_service

    async def mock_generate(**kwargs):
        raise Exception("No API key configured")

    monkeypatch.setattr(
        ai_service.AIGenerationService, "generate", mock_generate
    )
    resp = await client.post(
        "/api/v1/generate",
        json={"prompt": "Hello world", "type": "text"},
        headers=auth_headers,
    )
    # Should return 500 gracefully, not crash
    assert resp.status_code in (500, 429, 400)
