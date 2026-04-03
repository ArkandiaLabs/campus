# Arkandia Campus

The learning platform for [arkandia.co](https://arkandia.co). Lives at `campus.arkandia.co`.

Users who have purchased workshops can log in, watch recorded sessions, download resources, and track their progress.

## Stack

- **Backend:** FastAPI + asyncpg (Python 3.12), hexagonal architecture
- **Frontend:** Next.js 16 + Tailwind CSS 4 (TypeScript strict)
- **Auth:** Self-hosted Supabase Auth (GoTrue + Kong)
- **Database:** Self-hosted PostgreSQL (supabase/postgres image)
- **Infra:** Docker + Caddy on Hetzner

## Dev Setup

**Prerequisites:** Docker, pnpm (for running frontend checks locally), uv (for running backend checks locally)

1. Copy env file:
   ```bash
   cp .env.example .env
   # The defaults work out of the box for dev.
   # Change POSTGRES_PASSWORD and SUPABASE_JWT_SECRET for production.
   ```

2. Start all services (Postgres, GoTrue, Kong, backend, frontend):
   ```bash
   make dev
   ```

3. In a separate terminal, initialize the database (first time only):
   ```bash
   make db-init    # creates business tables + applies campus migrations
   make db-seed    # optional: sample content (edit cohort_id in seed.sql first)
   ```

4. Open the app:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Supabase Auth (Kong): http://localhost:8443

5. After registering a user, link them to a client record:
   ```bash
   make db-psql
   # Then run:
   # UPDATE core_client SET auth_user_id = '<id from auth.users>' WHERE email = '<email>';
   ```

### Regenerating the anon key

If you change `SUPABASE_JWT_SECRET`, regenerate the anon key:

```bash
cd backend && uv run python3 -c "
import jwt, time
secret = 'your-new-jwt-secret-here'
print(jwt.encode({'role':'anon','iss':'supabase','iat':int(time.time()),'exp':int(time.time())+315360000}, secret, algorithm='HS256'))
"
```

Paste the output into both `SUPABASE_ANON_KEY` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` in `.env`.

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
   docker build -t arkandia-campus-backend ./backend
   docker build -t arkandia-campus-frontend ./frontend
   ```

2. On the Hetzner VPS, create `.env` with production values:
   - Strong `POSTGRES_PASSWORD` and `SUPABASE_JWT_SECRET`
   - Regenerated `SUPABASE_ANON_KEY`
   - `SUPABASE_URL=https://campus.arkandia.co`
   - `SITE_URL=https://campus.arkandia.co`
   - `NEXT_PUBLIC_SUPABASE_URL=https://campus.arkandia.co`
   - SMTP settings for email confirmation (`GOTRUE_SMTP_*`)

3. Start:
   ```bash
   cd /opt/arkandia-campus
   docker compose -f infra/docker-compose.prod.yml up -d
   ```

4. Caddy handles HTTPS automatically via Let's Encrypt.

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
