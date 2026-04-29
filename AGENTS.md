# AGENTS.md

## Project overview

Campus is a workshop preparation environment for `campus.arkandia.co`, with:
- backend: FastAPI + asyncpg (hexagonal architecture)
- frontend: Next.js 16 + TypeScript strict
- auth: self-hosted Supabase Auth (GoTrue + Kong)
- infra: Docker Compose (dev + production variants)

This file is the operational playbook for agents. Use linked docs for deeper context.

## Where to find things

- **Architecture overview:** `docs/architecture.md`
- **Business / product context:** `docs/business.md`, `docs/target-user.md`
- **Dev setup and workflow:** `docs/development.md`, root `README.md`
- **Architecture decisions (why):** `docs/adrs/`
- **Database model:** `database/docs/data-model.md`, `database/README.md`
- **Infrastructure:** `infra/docs/infrastructure.md`
- **Design system (tokens, components, a11y):** `frontend/DESIGN.md` — authoritative for all UI work; consume semantic tokens, never invent values.

Read these before structural changes.

## Setup commands

```bash
cp .env.example .env
make hooks
make dev
make db-init
make db-seed
```

Reproducible dependency installs:

```bash
cd backend && uv sync --frozen
cd frontend && pnpm install --frozen-lockfile
```

## Checks to run

Fast local checks:

```bash
make check
```

CI-parity checks (recommended before merge):

```bash
make check
cd backend && uv run ruff format --check app tests && uv run lint-imports && uv audit
cd frontend && pnpm audit
```

## Change-based check matrix

- **Backend domain/service/repo/router:** `make check` + `cd backend && uv run lint-imports`
- **Frontend UI/app routes/data fetch:** `make check`
- **Dependency updates:** CI-parity checks including both `audit` commands
- **Database schema/migrations:** run `make db-init` in a fresh running stack and smoke test affected flows
- **Infra/deploy changes:** run `make check` and validate relevant compose/deploy commands

## Non-obvious rules

- **Hexagonal boundary:** `backend/app/domain` must never import from `backend/app/infrastructure`. Infrastructure implements domain `Protocol`s. Rationale: ADR-002.
- **Access-control invariant:** every query exposing offerings/content must filter by `core_purchase.status = 'completed'` AND `core_client.auth_user_id = <JWT sub>`.
- **Manual user linking:** GoTrue creates `auth.users` rows, but `core_client.auth_user_id` is not auto-populated. After signup: `UPDATE core_client SET auth_user_id = '<uuid>' WHERE email = '<email>';`
- **Migration workflow:** add SQL file to `database/migrations/` with next sequence number, then register it in `Makefile` under `db-migrate`.
- **Next.js 16:** check `frontend/node_modules/next/dist/docs/` when touching framework behavior.
- **Frontend conventions:** server components by default; user-facing text in Spanish (tuteo); server-side calls use internal URLs and browser calls use `NEXT_PUBLIC_*`.
- **`db-init` ordering:** GoTrue migrations must run before `baseline.sql`; `make dev` must be up first.
- **Design tokens are generated:** if you edit `frontend/DESIGN.md`, run `make tokens` and commit `frontend/src/app/tokens.css` and `frontend/src/design/tokens.json`. CI (`pnpm design:check`) fails if they drift.

## Testing conventions

Backend tests use fake in-memory repositories implementing domain `Protocol`s (not mocks, not live DB). Pattern: `backend/tests/test_catalog.py` (`FakeCatalogRepo`).

HTTP endpoint tests use `httpx.AsyncClient` + `ASGITransport`. `asyncio_mode = "auto"` is already set.

## Security

- Do not log JWTs, `SUPABASE_JWT_SECRET`, or `auth.users` rows.
- Do not commit `.env`; add new variables to `.env.example`.
