# Architecture

## Quality Attributes

| Priority | Attribute | Rationale |
|---|---|---|
| 1 | **Simplicity** | Hexagonal architecture with thin service layer. Easy to understand and modify for a small team. |
| 2 | **Deployability** | Single-server Docker Compose deployment. One `git pull && docker compose up` deploys everything. No cloud orchestration complexity. |
| 3 | **Modifiability** | Domain layer has zero framework imports. Swapping a repository requires only a new Protocol implementation. Frontend uses server components for easy data flow. |

## Architecture Patterns

### Backend: Hexagonal Architecture

The backend follows hexagonal (ports and adapters) architecture with two layers:

```
backend/app/
├── domain/              # Pure business logic — no framework deps
│   ├── models/          # Pydantic data schemas
│   ├── repositories/    # Abstract interfaces (Protocol)
│   └── services/        # Business logic calling repos
└── infrastructure/      # Framework-aware implementations
    ├── auth/            # JWT validation (JWTBearer)
    ├── persistence/     # asyncpg SQL repositories
    └── routers/         # FastAPI HTTP handlers
```

**Key rule:** Domain never imports from infrastructure. Infrastructure implements domain Protocols.

```mermaid
graph LR
    Router["Router (FastAPI)"] --> Service["Service (domain)"]
    Service --> RepoProtocol["Repository Protocol (domain)"]
    RepoProtocol -.->|implements| PgRepo["PgCatalogRepo (infrastructure)"]
    PgRepo --> DB[(PostgreSQL)]
```

Dependencies are injected via `app/dependencies.py`, which wires infrastructure implementations to domain Protocols.

### Frontend: Next.js App Router

- **Server components** are the default — used for dashboard, product detail, and all data-fetching pages
- **Client components** only where interactivity is required: login form, register form, navbar logout
- **Middleware** (`src/proxy.ts`) handles auth redirects: unauthenticated users go to `/login`, authenticated users on `/login` go to `/dashboard`
- **Dual URL pattern:** Server-side requests use Docker-internal URLs (`API_INTERNAL_URL`, `SUPABASE_INTERNAL_URL`); browser requests use public URLs (`NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SUPABASE_URL`)

## C4 Context Diagram

```mermaid
graph TB
    learner["<b>Learner</b><br/>[Person]<br/>Purchased a workshop on arkandia.co"]
    admin["<b>Admin</b><br/>[Person]<br/>Manages data via SQL"]

    campus["<b>Arkandia Campus</b><br/>[Software System]<br/>Learning portal where customers<br/>access purchased content"]

    arkandia_site["<b>arkandia.co</b><br/>[Software System]<br/>Marketing site that drives<br/>traffic and sales"]:::external
    lms["<b>External LMS Platforms</b><br/>[Software System]<br/>Gumroad, Hotmart — where<br/>purchases originate"]:::external

    learner -->|"Logs in, views offerings,<br/>accesses content"| campus
    admin -->|"Manages data via psql"| campus
    arkandia_site -->|"Links to checkout"| lms
    lms -->|"Purchase data synced<br/>to shared DB"| campus
    arkandia_site -->|"Directs buyers<br/>to Campus"| campus

    classDef external fill:#999,stroke:#666,color:#fff
```

## C4 Container Diagram

```mermaid
graph TB
    learner["<b>Learner</b><br/>[Person]<br/>Purchased a workshop on arkandia.co"]

    subgraph campus ["Arkandia Campus"]
        frontend["<b>Frontend</b><br/>[Container: Next.js 16, TypeScript]<br/>Serves pages, handles auth<br/>redirects via middleware"]
        backend["<b>Backend API</b><br/>[Container: FastAPI, Python 3.12]<br/>REST API with JWT validation<br/>and business logic"]
        auth["<b>Auth Service</b><br/>[Container: Supabase GoTrue]<br/>Handles signup, login,<br/>and token refresh"]
        db[("<b>Database</b><br/>[Container: PostgreSQL 15.6]<br/>Stores business data, auth<br/>schema, and RLS policies")]
    end

    learner -->|"Views pages"| frontend
    learner -->|"Authenticates"| auth
    frontend -->|"Fetches offerings<br/>and content"| backend
    frontend -->|"Validates sessions"| auth
    backend -->|"Reads and writes"| db
    auth -->|"Reads and writes"| db
```

## Tech Stack

| Layer | Technology | Version | Notes |
|---|---|---|---|
| Backend | FastAPI + asyncpg | Python 3.12 | Hexagonal arch, Protocol-based repos, `uv` for deps |
| Frontend | Next.js + React + Tailwind CSS | 16 / 19 / 4 | TypeScript strict, app router, `pnpm` for deps |
| Database | PostgreSQL | 15.6 (supabase image) | RLS enabled, raw SQL (no ORM) |
| Auth | Supabase GoTrue | v2.170.0 | Self-hosted, email + password, JWT (HS256) |
| API Gateway | Kong | 3.4 | Declarative config (no DB), routes `/auth/v1/*` |
| Reverse Proxy | Caddy | 2-alpine | Auto TLS via Let's Encrypt, production only |
| Dev tools | ruff, pyright, ESLint, vitest, pytest | — | `make check` runs all linters and tests |

