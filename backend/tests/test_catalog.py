from datetime import UTC, date, datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.domain.models.offering import ContentItem, OfferingDetail, UserOffering
from app.domain.services.catalog_service import CatalogService

# ─── Fake repository ──────────────────────────────────────────────────────────


class FakeCatalogRepo:
    def __init__(
        self,
        offerings: list[UserOffering] | None = None,
        detail: OfferingDetail | None = None,
    ) -> None:
        self._offerings = offerings or []
        self._detail = detail

    async def get_user_offerings(self, user_id: str) -> list[UserOffering]:
        return self._offerings

    async def get_offering_detail(self, user_id: str, offering_id: str) -> OfferingDetail | None:
        return self._detail


# ─── Fixtures ─────────────────────────────────────────────────────────────────

OFFERING_ID = uuid4()

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
    contents=[
        ContentItem(
            id=uuid4(),
            title="Sesion 1",
            description=None,
            content_type="video",
            content_url="https://vimeo.com/123",
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
