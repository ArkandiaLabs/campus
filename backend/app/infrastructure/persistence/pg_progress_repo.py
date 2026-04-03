import asyncpg

from app.domain.models.progress import ProgressRecord


class PgProgressRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def mark_complete(self, user_id: str, content_id: str) -> ProgressRecord:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO ed_content_progress (user_id, content_id)
                VALUES ($1, $2)
                ON CONFLICT (user_id, content_id) DO UPDATE
                    SET completed_at = ed_content_progress.completed_at
                RETURNING id, user_id, content_id, completed_at
                """,
                user_id,
                content_id,
            )
            return ProgressRecord(**dict(row))  # type: ignore[arg-type]

    async def unmark_complete(self, user_id: str, content_id: str) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM ed_content_progress
                WHERE user_id = $1 AND content_id = $2
                """,
                user_id,
                content_id,
            )

    async def user_has_access_to_content(self, user_id: str, content_id: str) -> bool:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 1
                FROM ed_content edc
                JOIN ed_cohort ec ON ec.id = edc.cohort_id
                JOIN core_purchase cp ON cp.cohort_id = ec.id
                JOIN core_client cc ON cc.id = cp.client_id
                WHERE edc.id = $1
                  AND cc.auth_user_id = $2
                  AND cp.status = 'completed'
                LIMIT 1
                """,
                content_id,
                user_id,
            )
            return row is not None
