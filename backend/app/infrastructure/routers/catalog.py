from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_catalog_service
from app.domain.models.offering import OfferingDetail, SessionDetail, UserOffering
from app.domain.services.catalog_service import CatalogService
from app.infrastructure.auth.jwt_bearer import jwt_bearer

router = APIRouter()


@router.get("/catalog", response_model=list[UserOffering])
async def list_catalog(
    user_id: str = Depends(jwt_bearer),
    service: CatalogService = Depends(get_catalog_service),
) -> list[UserOffering]:
    return await service.list_user_offerings(user_id)


@router.get("/catalog/sessions/{session_id}", response_model=SessionDetail)
async def get_session(
    session_id: str,
    user_id: str = Depends(jwt_bearer),
    service: CatalogService = Depends(get_catalog_service),
) -> SessionDetail:
    session = await service.get_session_detail(user_id, session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or not purchased.",
        )
    return session


@router.get("/catalog/{offering_id}", response_model=OfferingDetail)
async def get_offering(
    offering_id: str,
    user_id: str = Depends(jwt_bearer),
    service: CatalogService = Depends(get_catalog_service),
) -> OfferingDetail:
    offering = await service.get_offering(user_id, offering_id)
    if offering is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offering not found or not purchased.",
        )
    return offering
