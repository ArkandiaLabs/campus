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
                       ec.start_date, ec.end_date,
                       COUNT(DISTINCT edc.id) AS total_contents,
                       COUNT(DISTINCT edp.id) AS completed_contents
                FROM core_offering co
                JOIN core_purchase cp ON cp.offering_id = co.id
                JOIN core_client cc ON cc.id = cp.client_id
                LEFT JOIN ed_cohort ec ON ec.id = cp.cohort_id
                LEFT JOIN ed_content edc ON edc.cohort_id = ec.id
                LEFT JOIN ed_content_progress edp
                    ON edp.content_id = edc.id AND edp.user_id = $1
                WHERE cc.auth_user_id = $1
                  AND cp.status = 'completed'
                GROUP BY co.id, co.title, co.description, co.type, co.status,
                         cp.purchased_at, ec.title, ec.start_date, ec.end_date
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
                    total_contents=0,
                    completed_contents=0,
                )

            content_rows = await conn.fetch(
                """
                SELECT edc.id, edc.title, edc.description,
                       edc.content_type, edc.content_url,
                       edc.position, edc.is_preview,
                       (edp.id IS NOT NULL) AS completed
                FROM ed_content edc
                LEFT JOIN ed_content_progress edp
                    ON edp.content_id = edc.id AND edp.user_id = $1
                WHERE edc.cohort_id = $2
                ORDER BY edc.position ASC
                """,
                user_id,
                cohort_id,
            )

            contents = [ContentItem(**dict(row)) for row in content_rows]
            total = len(contents)
            completed = sum(1 for c in contents if c.completed)

            return OfferingDetail(
                id=offering_row["id"],
                title=offering_row["title"],
                description=offering_row["description"],
                cohort_title=offering_row["cohort_title"],
                start_date=offering_row["start_date"],
                end_date=offering_row["end_date"],
                contents=contents,
                total_contents=total,
                completed_contents=completed,
            )
