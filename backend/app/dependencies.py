from collections.abc import AsyncGenerator

import asyncpg
from fastapi import Depends

from app.db import get_pool
from app.domain.services.catalog_service import CatalogService
from app.infrastructure.persistence.pg_catalog_repo import PgCatalogRepository


async def get_catalog_service(
    pool: AsyncGenerator[asyncpg.Pool, None] = Depends(get_pool),
) -> CatalogService:
    return CatalogService(PgCatalogRepository(pool))  # type: ignore[arg-type]
