from datetime import UTC, date, datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.domain.models.offering import (
    ContentItem,
    OfferingDetail,
    SessionDetail,
    SessionSummary,
    UserOffering,
)
from app.domain.services.catalog_service import CatalogService
from tests.conftest import make_token

# ─── Fake repository ──────────────────────────────────────────────────────────


class FakeCatalogRepo:
    def __init__(
        self,
        offerings: list[UserOffering] | None = None,
        detail: OfferingDetail | None = None,
        session_detail: SessionDetail | None = None,
    ) -> None:
        self._offerings = offerings or []
        self._detail = detail
        self._session_detail = session_detail

    async def get_user_offerings(self, user_id: str) -> list[UserOffering]:
        return self._offerings

    async def get_offering_detail(self, user_id: str, offering_id: str) -> OfferingDetail | None:
        return self._detail

    async def get_session_detail(self, user_id: str, session_id: str) -> SessionDetail | None:
        return self._session_detail


# ─── Fixtures ─────────────────────────────────────────────────────────────────

OFFERING_ID = uuid4()
SESSION_ID = uuid4()

SAMPLE_OFFERING = UserOffering(
    id=OFFERING_ID,
    title="Workshop de IA",
    description="Un taller intensivo",
    type="workshop",
    status="published",
    cohort_title="Cohorte 1",
    start_date=date(2025, 1, 15),
    end_date=date(2025, 1, 19),
    purchased_at=datetime(2025, 1, 1, tzinfo=UTC),
)

SAMPLE_DETAIL = OfferingDetail(
    id=OFFERING_ID,
    title="Workshop de IA",
    description="Un taller intensivo",
    cohort_title="Cohorte 1",
    start_date=date(2025, 1, 15),
    end_date=date(2025, 1, 19),
    sessions=[
        SessionSummary(
            id=SESSION_ID,
            title="Sesión 1",
            scheduled_at=datetime(2025, 1, 15, 23, 0, tzinfo=UTC),
            duration_minutes=120,
        )
    ],
    general_resources=[
        ContentItem(
            id=uuid4(),
            title="Kit de configuración",
            description=None,
            content_type="download",
            content_url="https://storage.placeholder.co/kit.zip",
            position=1,
            is_preview=False,
        )
    ],
)

SAMPLE_SESSION_DETAIL = SessionDetail(
    id=SESSION_ID,
    title="Sesión 1",
    description=None,
    scheduled_at=datetime(2025, 1, 15, 23, 0, tzinfo=UTC),
    duration_minutes=120,
    contents=[
        ContentItem(
            id=uuid4(),
            title="Grabación de la Sesión",
            description=None,
            content_type="video",
            content_url="https://vimeo.com/100000001",
            position=1,
            is_preview=True,
        )
    ],
)


# ─── Service tests ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_user_offerings_returns_offerings() -> None:
    repo = FakeCatalogRepo(offerings=[SAMPLE_OFFERING])
    service = CatalogService(repo)
    result = await service.list_user_offerings("user-123")
    assert result == [SAMPLE_OFFERING]


@pytest.mark.asyncio
async def test_list_user_offerings_empty() -> None:
    repo = FakeCatalogRepo()
    service = CatalogService(repo)
    result = await service.list_user_offerings("user-123")
    assert result == []


@pytest.mark.asyncio
async def test_get_offering_returns_detail() -> None:
    repo = FakeCatalogRepo(detail=SAMPLE_DETAIL)
    service = CatalogService(repo)
    result = await service.get_offering("user-123", str(OFFERING_ID))
    assert result == SAMPLE_DETAIL


@pytest.mark.asyncio
async def test_get_offering_not_found() -> None:
    repo = FakeCatalogRepo(detail=None)
    service = CatalogService(repo)
    result = await service.get_offering("user-123", str(uuid4()))
    assert result is None


@pytest.mark.asyncio
async def test_get_offering_returns_sessions_and_general_resources() -> None:
    detail = OfferingDetail(
        id=OFFERING_ID,
        title="Workshop de IA",
        description=None,
        cohort_title="Cohorte 1",
        start_date=None,
        end_date=None,
        sessions=[
            SessionSummary(
                id=uuid4(),
                title="Sesión 1",
                scheduled_at=datetime(2025, 1, 15, 23, 0, tzinfo=UTC),
                duration_minutes=120,
            )
        ],
        general_resources=[
            ContentItem(
                id=uuid4(),
                title="Kit de configuración",
                description=None,
                content_type="download",
                content_url="https://storage.placeholder.co/kit.zip",
                position=1,
                is_preview=False,
            )
        ],
    )
    repo = FakeCatalogRepo(detail=detail)
    service = CatalogService(repo)
    result = await service.get_offering("user-123", str(OFFERING_ID))
    assert result is not None
    assert len(result.sessions) == 1
    assert result.sessions[0].title == "Sesión 1"
    assert result.sessions[0].duration_minutes == 120
    assert len(result.general_resources) == 1
    assert result.general_resources[0].content_type == "download"


@pytest.mark.asyncio
async def test_get_offering_no_cohort_returns_empty_lists() -> None:
    detail = OfferingDetail(
        id=OFFERING_ID,
        title="Workshop de IA",
        description=None,
        cohort_title=None,
        start_date=None,
        end_date=None,
        sessions=[],
        general_resources=[],
    )
    repo = FakeCatalogRepo(detail=detail)
    service = CatalogService(repo)
    result = await service.get_offering("user-123", str(OFFERING_ID))
    assert result is not None
    assert result.sessions == []
    assert result.general_resources == []


# ─── HTTP endpoint tests (health check only — no DB required) ─────────────────


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_catalog_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/catalog")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_catalog_rejects_invalid_token(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/catalog",
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_catalog_detail_requires_auth(client: AsyncClient) -> None:
    offering_id = str(uuid4())
    response = await client.get(f"/api/v1/catalog/{offering_id}")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_health_check_no_auth_required(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_check_rejects_post(client: AsyncClient) -> None:
    response = await client.post("/api/v1/health")
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_catalog_rejects_expired_token(client: AsyncClient) -> None:
    token = make_token(expired=True)
    response = await client.get(
        "/api/v1/catalog",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired."


@pytest.mark.asyncio
async def test_catalog_detail_rejects_expired_token(client: AsyncClient) -> None:
    token = make_token(expired=True)
    response = await client.get(
        f"/api/v1/catalog/{uuid4()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired."


@pytest.mark.asyncio
async def test_catalog_detail_response_has_sessions_and_general_resources() -> None:
    from app.dependencies import get_catalog_service
    from app.main import create_app

    app = create_app()
    app.dependency_overrides[get_catalog_service] = lambda: CatalogService(
        FakeCatalogRepo(detail=SAMPLE_DETAIL)
    )

    token = make_token()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            f"/api/v1/catalog/{OFFERING_ID}",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert "general_resources" in data
    assert "contents" not in data
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["title"] == "Sesión 1"
    assert len(data["general_resources"]) == 1
    assert data["general_resources"][0]["content_type"] == "download"


# ─── Session detail service tests ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_session_detail_returns_detail() -> None:
    repo = FakeCatalogRepo(session_detail=SAMPLE_SESSION_DETAIL)
    service = CatalogService(repo)
    result = await service.get_session_detail("user-123", str(SESSION_ID))
    assert result == SAMPLE_SESSION_DETAIL


@pytest.mark.asyncio
async def test_get_session_detail_not_found() -> None:
    repo = FakeCatalogRepo(session_detail=None)
    service = CatalogService(repo)
    result = await service.get_session_detail("user-123", str(uuid4()))
    assert result is None


# ─── Session detail HTTP tests ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_session_detail_requires_auth(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/catalog/sessions/{SESSION_ID}")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_session_detail_returns_200_with_contents() -> None:
    from app.dependencies import get_catalog_service
    from app.main import create_app

    app = create_app()
    app.dependency_overrides[get_catalog_service] = lambda: CatalogService(
        FakeCatalogRepo(session_detail=SAMPLE_SESSION_DETAIL)
    )

    token = make_token()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            f"/api/v1/catalog/sessions/{SESSION_ID}",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(SESSION_ID)
    assert data["title"] == "Sesión 1"
    assert "contents" in data
    # Must return SessionDetail shape, not OfferingDetail shape
    assert "sessions" not in data
    assert "general_resources" not in data
    assert len(data["contents"]) == 1
    assert data["contents"][0]["content_type"] == "video"


@pytest.mark.asyncio
async def test_session_detail_returns_404_when_not_found_or_not_purchased() -> None:
    from app.dependencies import get_catalog_service
    from app.main import create_app

    app = create_app()
    app.dependency_overrides[get_catalog_service] = lambda: CatalogService(
        FakeCatalogRepo(session_detail=None)
    )

    token = make_token()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            f"/api/v1/catalog/sessions/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found or not purchased."
