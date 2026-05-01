import asyncpg

from app.domain.models.offering import (
    ContentItem,
    OfferingDetail,
    SessionDetail,
    SessionSummary,
    UserOffering,
)


class PgCatalogRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def get_user_offerings(self, user_id: str) -> list[UserOffering]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT co.id, co.title, co.description, co.type, co.status,
                       cp.purchased_at,
                       ec.title AS cohort_title,
                       ec.start_date, ec.end_date
                FROM core_offering co
                JOIN core_purchase cp ON cp.offering_id = co.id
                JOIN core_client cc ON cc.id = cp.client_id
                LEFT JOIN ed_cohort ec ON ec.id = cp.cohort_id
                WHERE cc.auth_user_id = $1
                  AND cp.status = 'completed'
                ORDER BY cp.purchased_at DESC
                """,
                user_id,
            )
            return [UserOffering(**dict(row)) for row in rows]

    async def get_offering_detail(self, user_id: str, offering_id: str) -> OfferingDetail | None:
        async with self._pool.acquire() as conn:
            offering_row = await conn.fetchrow(
                """
                SELECT co.id, co.title, co.description,
                       ec.title AS cohort_title,
                       ec.start_date, ec.end_date,
                       ec.id AS cohort_id
                FROM core_offering co
                JOIN core_purchase cp ON cp.offering_id = co.id
                JOIN core_client cc ON cc.id = cp.client_id
                LEFT JOIN ed_cohort ec ON ec.id = cp.cohort_id
                WHERE cc.auth_user_id = $1
                  AND co.id = $2
                  AND cp.status = 'completed'
                LIMIT 1
                """,
                user_id,
                offering_id,
            )

            if offering_row is None:
                return None

            cohort_id = offering_row["cohort_id"]

            if cohort_id is None:
                return OfferingDetail(
                    id=offering_row["id"],
                    title=offering_row["title"],
                    description=offering_row["description"],
                    cohort_title=offering_row["cohort_title"],
                    start_date=offering_row["start_date"],
                    end_date=offering_row["end_date"],
                    sessions=[],
                    general_resources=[],
                )

            session_rows = await conn.fetch(
                """
                SELECT id, title, scheduled_at, duration_minutes
                FROM ed_session
                WHERE cohort_id = $1
                ORDER BY scheduled_at ASC NULLS LAST, id ASC
                """,
                cohort_id,
            )

            resource_rows = await conn.fetch(
                """
                SELECT edc.id, edc.title, edc.description,
                       edc.content_type, edc.content_url,
                       edc.position, edc.is_preview
                FROM ed_content edc
                WHERE edc.cohort_id = $1
                  AND edc.session_id IS NULL
                ORDER BY edc.position ASC
                """,
                cohort_id,
            )

            return OfferingDetail(
                id=offering_row["id"],
                title=offering_row["title"],
                description=offering_row["description"],
                cohort_title=offering_row["cohort_title"],
                start_date=offering_row["start_date"],
                end_date=offering_row["end_date"],
                sessions=[SessionSummary(**dict(row)) for row in session_rows],
                general_resources=[ContentItem(**dict(row)) for row in resource_rows],
            )

    async def get_session_detail(self, user_id: str, session_id: str) -> SessionDetail | None:
        async with self._pool.acquire() as conn:
            session_row = await conn.fetchrow(
                """
                SELECT es.id, es.title, es.description,
                       es.scheduled_at, es.duration_minutes,
                       es.cohort_id
                FROM ed_session es
                JOIN ed_cohort ec ON ec.id = es.cohort_id
                JOIN core_purchase cp ON cp.cohort_id = ec.id
                                     AND cp.status = 'completed'
                JOIN core_client cc ON cc.id = cp.client_id
                                   AND cc.auth_user_id = $2
                WHERE es.id = $1
                LIMIT 1
                """,
                session_id,
                user_id,
            )

            if session_row is None:
                return None

            content_rows = await conn.fetch(
                """
                SELECT id, title, description, content_type, content_url, position, is_preview
                FROM ed_content
                WHERE session_id = $1
                  AND cohort_id = $2
                ORDER BY position ASC, id ASC
                """,
                session_id,
                session_row["cohort_id"],
            )

            return SessionDetail(
                id=session_row["id"],
                title=session_row["title"],
                description=session_row["description"],
                scheduled_at=session_row["scheduled_at"],
                duration_minutes=session_row["duration_minutes"],
                contents=[ContentItem(**dict(row)) for row in content_rows],
            )
