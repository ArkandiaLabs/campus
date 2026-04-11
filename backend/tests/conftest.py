import os
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from httpx import ASGITransport, AsyncClient

TEST_JWT_SECRET = "test-secret-at-least-32-chars-long!!"

# Set required env vars before importing the app
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
os.environ.setdefault("SUPABASE_JWT_SECRET", TEST_JWT_SECRET)
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("BACKEND_CORS_ORIGINS", "http://localhost:3000")

from app.main import create_app  # noqa: E402


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


def make_token(
    sub: str = "user-123",
    expired: bool = False,
    aud: str = "authenticated",
) -> str:
    now = datetime.now(UTC)
    exp = now - timedelta(hours=1) if expired else now + timedelta(hours=1)
    return jwt.encode(  # type: ignore[reportUnknownMemberType]
        {"sub": sub, "aud": aud, "iat": now, "exp": exp},
        TEST_JWT_SECRET,
        algorithm="HS256",
    )
