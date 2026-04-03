from app.domain.models.offering import OfferingDetail, UserOffering
from app.domain.repositories.catalog_repo import CatalogRepository


class CatalogService:
    def __init__(self, repo: CatalogRepository) -> None:
        self._repo = repo

    async def list_user_offerings(self, user_id: str) -> list[UserOffering]:
        return await self._repo.get_user_offerings(user_id)

    async def get_offering(self, user_id: str, offering_id: str) -> OfferingDetail | None:
        return await self._repo.get_offering_detail(user_id, offering_id)
