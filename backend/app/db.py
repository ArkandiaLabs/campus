from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any

import asyncpg

if TYPE_CHECKING:
    PoolType = asyncpg.Pool[Any]
else:
    PoolType = asyncpg.Pool

_pool: PoolType | None = None


async def create_pool(dsn: str) -> PoolType:
    return await asyncpg.create_pool(dsn=dsn)  # type: ignore[return-value]


async def close_pool(pool: PoolType) -> None:
    await pool.close()


def set_pool(pool: PoolType) -> None:
    global _pool
    _pool = pool


async def get_pool() -> AsyncGenerator[PoolType, None]:
    if _pool is None:
        raise RuntimeError("Database pool not initialized")
    yield _pool
