from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.domain.models.progress import ProgressRecord
from app.domain.services.progress_service import ProgressService

# ─── Fake repository ──────────────────────────────────────────────────────────


class FakeProgressRepo:
    def __init__(self, has_access: bool = True) -> None:
        self._has_access = has_access
        self.marked: list[tuple[str, str]] = []
        self.unmarked: list[tuple[str, str]] = []

    async def mark_complete(self, user_id: str, content_id: str) -> ProgressRecord:
        self.marked.append((user_id, content_id))
        return ProgressRecord(
            id=uuid4(),
            user_id=uuid4(),
            content_id=uuid4(),
            completed_at=datetime(2025, 1, 1, tzinfo=UTC),
        )

    async def unmark_complete(self, user_id: str, content_id: str) -> None:
        self.unmarked.append((user_id, content_id))

    async def user_has_access_to_content(self, user_id: str, content_id: str) -> bool:
        return self._has_access


# ─── Service tests ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_mark_complete_with_access() -> None:
    repo = FakeProgressRepo(has_access=True)
    service = ProgressService(repo)
    result = await service.mark_complete("user-1", str(uuid4()))
    assert isinstance(result, ProgressRecord)
    assert len(repo.marked) == 1


@pytest.mark.asyncio
async def test_mark_complete_without_access_raises_403() -> None:
    repo = FakeProgressRepo(has_access=False)
    service = ProgressService(repo)
    with pytest.raises(HTTPException) as exc_info:
        await service.mark_complete("user-1", str(uuid4()))
    assert exc_info.value.status_code == 403
    assert len(repo.marked) == 0


@pytest.mark.asyncio
async def test_unmark_complete_delegates_to_repo() -> None:
    repo = FakeProgressRepo()
    service = ProgressService(repo)
    content_id = str(uuid4())
    await service.unmark_complete("user-1", content_id)
    assert repo.unmarked == [("user-1", content_id)]


# ─── HTTP endpoint tests ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_progress_post_requires_auth(client: object) -> None:
    from httpx import AsyncClient

    assert isinstance(client, AsyncClient)
    response = await client.post("/api/v1/progress", json={"content_id": str(uuid4())})
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_progress_delete_requires_auth(client: object) -> None:
    from httpx import AsyncClient

    assert isinstance(client, AsyncClient)
    response = await client.delete(f"/api/v1/progress/{uuid4()}")
    assert response.status_code in (401, 403)
