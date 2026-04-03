from fastapi import HTTPException, status

from app.domain.models.progress import ProgressRecord
from app.domain.repositories.progress_repo import ProgressRepository


class ProgressService:
    def __init__(self, repo: ProgressRepository) -> None:
        self._repo = repo

    async def mark_complete(self, user_id: str, content_id: str) -> ProgressRecord:
        has_access = await self._repo.user_has_access_to_content(user_id, content_id)
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this content.",
            )
        return await self._repo.mark_complete(user_id, content_id)

    async def unmark_complete(self, user_id: str, content_id: str) -> None:
        await self._repo.unmark_complete(user_id, content_id)
