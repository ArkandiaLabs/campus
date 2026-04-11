# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make dev          # start all services (Postgres, GoTrue, Kong, backend, frontend)
make build        # build Docker images
make db-init      # baseline schema + all migrations (first time only)
make db-seed      # load sample data
make db-psql      # interactive psql in container
make lint         # ruff + eslint
make typecheck    # pyright + tsc
make test         # pytest + vitest
make check        # lint + typecheck + test
```

### Single test (backend)
```bash
cd backend && uv run pytest tests/test_catalog.py -v
```

### Single test (frontend)
```bash
cd frontend && pnpm vitest run src/lib/__tests__/foo.test.ts
```

## Architecture

### Backend — hexagonal (FastAPI + asyncpg)

`domain/` never imports from `infrastructure/`. Infrastructure implements domain Protocols.

- `domain/models/` — Pydantic schemas (the only data contracts shared across layers)
- `domain/repositories/` — `Protocol` interfaces (e.g. `CatalogRepository`)
- `domain/services/` — business logic; receives a repo via constructor, calls its methods
- `infrastructure/persistence/` — asyncpg SQL implementations of domain repos
- `infrastructure/auth/` — JWT validation (HS256 via PyJWT against `SUPABASE_JWT_SECRET`)
- `infrastructure/routers/` — FastAPI route handlers; inject services via `dependencies.py`
- `dependencies.py` — wires `PgCatalogRepository` → `CatalogService` via FastAPI `Depends`

Adding a new feature: define models → define Protocol → implement service → implement pg repo → add router → wire in `dependencies.py`.

Tests use a `FakeCatalogRepo` (in-memory struct implementing the Protocol), never hit a real DB.

### Frontend — Next.js (App Router)

> **Read `node_modules/next/dist/docs/` before writing any code** — this version may have breaking changes from training data.

- Server components (e.g. `app/dashboard/page.tsx`) fetch from backend using `API_INTERNAL_URL` (Docker network) and Supabase server client for auth.
- Client components (e.g. `src/lib/api.ts`) use `NEXT_PUBLIC_API_URL` and get JWT from the Supabase browser client.
- Auth is Supabase GoTrue. Two separate clients: `supabase-server.ts` (server/SSR) and `supabase-browser.ts` (client components).
- `src/types/` — shared TypeScript types that mirror backend Pydantic models.

### Database

Manual SQL migrations in `database/migrations/`, applied in order by `make db-migrate`. No ORM. Schema baseline in `database/schema/baseline.sql`.

After registering a user, link them to `core_client` manually:
```sql
UPDATE core_client SET auth_user_id = '<uuid>' WHERE email = '<email>';
```

### Services layout (Docker Compose)

| Service | Port | Purpose |
|---------|------|---------|
| db | 5432 | PostgreSQL (supabase/postgres image) |
| gotrue | (internal) | Auth server |
| kong | 8443 | Auth gateway (routes to gotrue) |
| backend | 8000 | FastAPI |
| frontend | 3000 | Next.js |

Frontend SSR uses `SUPABASE_INTERNAL_URL=http://kong:8000` and `API_INTERNAL_URL=http://backend:8000` (Docker network). Browser uses `NEXT_PUBLIC_*` env vars pointing to localhost.
