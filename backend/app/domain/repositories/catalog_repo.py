from typing import Protocol

from app.domain.models.offering import OfferingDetail, UserOffering


class CatalogRepository(Protocol):
    async def get_user_offerings(self, user_id: str) -> list[UserOffering]: ...

    async def get_offering_detail(
        self, user_id: str, offering_id: str
    ) -> OfferingDetail | None: ...
