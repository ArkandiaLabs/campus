import asyncpg

from app.domain.models.offering import ContentItem, OfferingDetail, UserOffering


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
                    contents=[],
                )

            content_rows = await conn.fetch(
                """
                SELECT edc.id, edc.title, edc.description,
                       edc.content_type, edc.content_url,
                       edc.position, edc.is_preview
                FROM ed_content edc
                WHERE edc.cohort_id = $1
                ORDER BY edc.position ASC
                """,
                cohort_id,
            )

            contents = [ContentItem(**dict(row)) for row in content_rows]

            return OfferingDetail(
                id=offering_row["id"],
                title=offering_row["title"],
                description=offering_row["description"],
                cohort_title=offering_row["cohort_title"],
                start_date=offering_row["start_date"],
                end_date=offering_row["end_date"],
                contents=contents,
            )
