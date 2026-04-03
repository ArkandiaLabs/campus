from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_progress_service
from app.domain.models.progress import ProgressCreate, ProgressRecord
from app.domain.services.progress_service import ProgressService
from app.infrastructure.auth.jwt_bearer import jwt_bearer

router = APIRouter()


@router.post("/progress", response_model=ProgressRecord, status_code=status.HTTP_201_CREATED)
async def mark_complete(
    body: ProgressCreate,
    user_id: str = Depends(jwt_bearer),
    service: ProgressService = Depends(get_progress_service),
) -> ProgressRecord:
    return await service.mark_complete(user_id, str(body.content_id))


@router.delete("/progress/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unmark_complete(
    content_id: str,
    user_id: str = Depends(jwt_bearer),
    service: ProgressService = Depends(get_progress_service),
) -> Response:
    await service.unmark_complete(user_id, content_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
