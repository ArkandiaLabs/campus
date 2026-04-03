from typing import Protocol

from app.domain.models.progress import ProgressRecord


class ProgressRepository(Protocol):
    async def mark_complete(self, user_id: str, content_id: str) -> ProgressRecord: ...

    async def unmark_complete(self, user_id: str, content_id: str) -> None: ...

    async def user_has_access_to_content(self, user_id: str, content_id: str) -> bool: ...
