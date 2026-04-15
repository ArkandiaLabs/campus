# AGENTS.md

Guidance for AI coding agents working in this repo. Follows the [agents.md](https://agents.md) convention.

This file only captures what isn't obvious from the code or existing docs. For architecture, data model, ADRs, and broader context, follow the pointers below and read the source.

## Where to find things

- **Architecture overview:** `docs/architecture.md`
- **Business / product context:** `docs/business.md`, `docs/target-user.md`
- **Dev environment setup:** `docs/development.md`, root `README.md`
- **Architecture decisions (why, not what):** `docs/adrs/`
- **Database schema + relationships:** `database/docs/data-model.md`, `database/README.md`
- **Infrastructure:** `infra/docs/infrastructure.md`

Read these before making structural changes.

## Commands

```bash
make dev          # start all services (Postgres, GoTrue, Kong, backend, frontend)
make check        # lint + typecheck + test (all) — run before declaring work done
make db-init      # baseline schema + migrations; requires `make dev` running first
make db-seed      # sample data
make db-psql      # psql inside the db container
```

Scoped runs: `cd backend && uv run pytest -v` / `uv run ruff check app tests` / `uv run pyright`.
Frontend: `cd frontend && pnpm vitest run` / `pnpm eslint src` / `pnpm tsc --noEmit`.

## Non-obvious rules

- **Hexagonal boundary:** `backend/app/domain` must never import from `backend/app/infrastructure`. Infrastructure implements domain `Protocol`s. Rationale: ADR-002.
- **Access-control invariant:** every query that exposes offerings/content must filter by `core_purchase.status = 'completed'` AND `core_client.auth_user_id = <JWT sub>`. Do not add endpoints that bypass this.
- **Manual user linking:** GoTrue creates `auth.users` rows, but `core_client.auth_user_id` is not auto-populated. After registering a new user: `UPDATE core_client SET auth_user_id = '<uuid>' WHERE email = '<email>';`
- **Next.js 16:** this project uses Next.js 16, which has breaking changes vs. earlier versions. Your training data is likely wrong. Read `frontend/node_modules/next/dist/docs/` before writing Next.js-specific code. Heed deprecation notices.
- **`db-init` ordering:** GoTrue must have run its own migrations before `baseline.sql` executes, so `make dev` must be up first.

## Testing

Backend tests use **fake in-memory repositories implementing the domain `Protocol`** — not mocks, not a live DB. Pattern: see `backend/tests/test_catalog.py` (`FakeCatalogRepo`). HTTP endpoint tests use `httpx.AsyncClient` + `ASGITransport`. `asyncio_mode = "auto"` is set, so new tests don't need `@pytest.mark.asyncio`.

## Code style

Enforced by tooling — run `make lint` and `make typecheck`. Don't add docstrings, comments, or type annotations to code you didn't change.

## Security

- Don't log JWTs, `SUPABASE_JWT_SECRET`, or `auth.users` rows.
- Don't commit `.env`; add new variables to `.env.example`.
