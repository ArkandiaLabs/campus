# Development Guide

## Prerequisites

- **Docker** and Docker Compose
- **pnpm** — frontend package manager
- **uv** — Python package manager (for backend)
- **Lefthook** — git hooks manager (`brew install lefthook`)

## Dev Workflow

```bash
# 1. Clone and configure
cp .env.example .env          # defaults work for local dev

# 2. Install git hooks (one-time)
make hooks

# 3. Start all services
make dev                       # db, gotrue, kong, backend, frontend

# 4. Initialize database (first time only, in a separate terminal)
make db-init                   # baseline schema + migrations
make db-seed                   # optional: sample content

# 5. Register a user at http://localhost:3000/register

# 6. Link the auth user to a client record
make db-psql
# UPDATE core_client SET auth_user_id = '<id from auth.users>' WHERE email = '<email>';

# 7. Log in at http://localhost:3000/login
```

### Service URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Supabase Auth (Kong) | http://localhost:8443 |
| Database | `make db-psql` |

## Running Checks

All checks at once:

```bash
make check
```

### Backend

```bash
cd backend
uv run ruff check app tests    # linting
uv run pyright                  # type checking
uv run pytest -v                # tests
```

### Frontend

```bash
cd frontend
pnpm eslint src                 # linting
pnpm tsc --noEmit               # type checking
pnpm vitest run                 # tests
pnpm design:lint                # validate frontend/DESIGN.md
pnpm design:check               # detect drift between DESIGN.md and tokens.css
```

## UI development

The UI is governed by `frontend/DESIGN.md` (warm amber + sapphire system, Aleo headlines, Rubik body).

```bash
make tokens                     # regenerate tokens.css from DESIGN.md
```

**Modifying the design system:**

1. Edit `frontend/DESIGN.md` (frontmatter for tokens, prose for rationale).
2. Run `make tokens` to regenerate `frontend/src/design/tokens.json` (via `@google/design.md` CLI) and `frontend/src/app/tokens.css` (Tailwind v4 `@theme` block).
3. Commit all three files. CI (`pnpm design:check`) blocks PRs where the generated files drift from DESIGN.md.

## Adding a New Feature

### Backend (Hexagonal Architecture)

Follow this order to maintain the domain/infrastructure separation:

1. **Domain model** — add a Pydantic schema in `backend/app/domain/models/`
2. **Repository Protocol** — define the interface in `backend/app/domain/repositories/`
3. **Service** — implement business logic in `backend/app/domain/services/` using the Protocol
4. **Repository implementation** — write SQL in `backend/app/infrastructure/persistence/`
5. **Router** — create FastAPI endpoints in `backend/app/infrastructure/routers/`
6. **Wire up** — register the router in `backend/app/main.py` and add dependency injection in `backend/app/dependencies.py`

### Frontend

1. **TypeScript types** — mirror backend models in `frontend/src/types/index.ts`
2. **API method** — add a typed fetch function in `frontend/src/lib/api.ts`
3. **Page** — create a route in `frontend/src/app/` (server component by default)
4. **Components** — extract reusable UI into `frontend/src/components/`

### Database

Write a migration file in `database/migrations/` with the next sequence number:

```
database/migrations/006_your_migration_name.sql
```

Add the execution line to `Makefile` under the `db-migrate` target.

## Key Conventions

### Backend

- **Domain isolation:** `domain/` must never import from `infrastructure/`. No FastAPI, asyncpg, or framework imports in domain code.
- **Protocol-based repos:** Repositories are defined as `typing.Protocol` classes, not abstract base classes.
- **Raw SQL:** All queries live in `infrastructure/persistence/`. No ORM.
- **Async-first:** Use `async/await` everywhere. Database calls use asyncpg connection pools.
- **Pydantic models:** Domain models are Pydantic `BaseModel` subclasses for validation and serialization.

### Frontend

- **Server components by default:** Only use `"use client"` when the component needs browser APIs or interactivity (forms, event handlers).
- **Dual URL pattern:** Server-side code uses `API_INTERNAL_URL` and `SUPABASE_INTERNAL_URL` (Docker-internal). Browser code uses `NEXT_PUBLIC_*` URLs.
- **Spanish UI:** All user-facing text is in Spanish (es-CO locale). Use "tuteo" (informal *tu*).
- **ESLint v9:** Flat config in `frontend/eslint.config.mjs`. ESLint v10 is not compatible with eslint-plugin-react v7.

### Database

- All primary keys are `uuid DEFAULT gen_random_uuid()`
- All tables have `created_at` and `updated_at` as `timestamptz NOT NULL DEFAULT now()`
- Use enum types for constrained values
- Write RLS policies for tables accessed by end users
- Migrations are sequential and idempotent where possible
