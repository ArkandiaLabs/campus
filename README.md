# Arkandia Campus

The learning platform for [arkandia.co](https://arkandia.co). Lives at `campus.arkandia.co`.

Users who have purchased workshops can log in, watch recorded sessions, download resources, and track their progress.

## Stack

- **Backend:** FastAPI + asyncpg (Python 3.12), hexagonal architecture
- **Frontend:** Next.js 16 + Tailwind CSS 4 (TypeScript strict)
- **Auth:** Supabase Auth (JWT)
- **Database:** PostgreSQL via Supabase
- **Infra:** Docker + Caddy on Hetzner

## Dev Setup

**Prerequisites:** Python 3.12+, Node 20+, pnpm, uv, Docker

1. Copy env file:
   ```bash
   cp .env.example .env
   # Fill in SUPABASE_URL, SUPABASE_JWT_SECRET, DATABASE_URL,
   # NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY
   ```

2. Apply database migrations to your dev Supabase project:
   ```bash
   # See database/README.md for full instructions
   psql $DATABASE_URL -f database/migrations/001_add_auth_user_id_to_core_client.sql
   psql $DATABASE_URL -f database/migrations/002_create_ed_content.sql
   psql $DATABASE_URL -f database/migrations/003_create_ed_content_progress.sql
   psql $DATABASE_URL -f database/migrations/004_enable_rls_campus.sql
   ```

3. Seed sample content (update cohort_id first — see `database/seeds/seed.sql`):
   ```bash
   psql $DATABASE_URL -f database/seeds/seed.sql
   ```

4. Link a Supabase Auth user to a client record (after registering):
   ```sql
   UPDATE core_client SET auth_user_id = '<auth.users id>' WHERE email = '<email>';
   ```

5. Start dev servers:
   ```bash
   make dev
   ```
   Backend: http://localhost:8000  
   Frontend: http://localhost:3000

## Running Checks

```bash
make lint        # ruff + eslint
make typecheck   # pyright + tsc
make test        # pytest + vitest
make check       # all three
```

### Backend only

```bash
cd backend
uv run pytest -v
uv run ruff check app tests
uv run pyright
```

### Frontend only

```bash
cd frontend
pnpm eslint src
pnpm tsc --noEmit
pnpm vitest run
```

## Deploying to Production

1. Build images on the server (or push from CI):
   ```bash
   make build
   # or
   docker build -t arkandia-campus-backend ./backend
   docker build -t arkandia-campus-frontend ./frontend
   ```

2. On the Hetzner VPS:
   ```bash
   cd /opt/arkandia-campus
   # Ensure .env is populated
   docker compose -f infra/docker-compose.prod.yml up -d
   ```

3. Caddy handles HTTPS automatically via Let's Encrypt.

## Architecture

```
backend/app/
├── domain/          # Pure business logic — no framework deps
│   ├── models/      # Pydantic schemas
│   ├── repositories/ # Abstract interfaces (Protocol)
│   └── services/    # Business logic calling repos
└── infrastructure/  # Framework-aware implementations
    ├── auth/        # JWT validation
    ├── persistence/ # asyncpg SQL repositories
    └── routers/     # FastAPI HTTP handlers
```

Domain never imports from infrastructure. Infrastructure implements domain Protocols.

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/health` | No | Health check |
| GET | `/api/v1/catalog` | Yes | List purchased offerings |
| GET | `/api/v1/catalog/{id}` | Yes | Offering detail + content |
| POST | `/api/v1/progress` | Yes | Mark content complete |
| DELETE | `/api/v1/progress/{id}` | Yes | Unmark content |
