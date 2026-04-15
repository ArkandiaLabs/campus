# ADR-002: Hexagonal Architecture for Backend

## Status

Accepted

## Context

The backend serves a REST API for the Campus frontend. It needs to:

- Validate JWT tokens and extract user identity
- Query PostgreSQL for purchased offerings and content
- Return typed JSON responses

Options considered:

1. **Flat FastAPI app** — all logic in route handlers, quick to build
2. **Hexagonal / ports-and-adapters** — domain logic separated from infrastructure
3. **Full DDD** — aggregates, value objects, domain events — full tactical patterns

The codebase is small (~20 files) and maintained by a small team. Over-engineering is a real risk. But Arkandia teaches software architecture — the codebase itself should demonstrate clean separation.

## Decision

Use hexagonal architecture with Protocol-based repositories.

```
backend/app/
├── domain/           # Zero framework imports
│   ├── models/       # Pydantic schemas
│   ├── repositories/ # typing.Protocol interfaces
│   └── services/     # Business logic
└── infrastructure/   # Framework-aware
    ├── auth/         # JWT validation
    ├── persistence/  # asyncpg implementations
    └── routers/      # FastAPI handlers
```

Key rules:
- Domain layer must not import from infrastructure
- Repositories are `typing.Protocol` classes (not ABCs)
- Dependencies are injected via `app/dependencies.py`
- Raw SQL lives exclusively in `infrastructure/persistence/`

## Consequences

**Easier:**
- Domain logic is testable without a database (use fake repos)
- Swapping persistence (e.g., from asyncpg to SQLAlchemy) requires only a new repo implementation
- Clear mental model: "where does this code go?" always has an answer
- Demonstrates architecture principles that align with Arkandia's educational mission

**More difficult:**
- More files and indirection than a flat FastAPI app for a small codebase
- Protocol-based repos require explicit type annotations that add boilerplate
- New contributors must understand the layering rules before making changes
