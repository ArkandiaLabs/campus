# ADR-001: Self-Hosted Supabase Auth

## Status

Accepted

## Context

Campus needs user authentication (registration, login, session management, JWT tokens). Options considered:

1. **Supabase Cloud** — managed auth service, zero infrastructure
2. **Self-hosted Supabase** (GoTrue + Kong) — same APIs, self-managed
3. **Custom auth** — build from scratch with something like FastAPI-Users or Authlib

Campus already uses a self-hosted PostgreSQL database (supabase/postgres image) for business data. The Supabase client libraries (`@supabase/ssr`) provide good Next.js integration for cookie-based sessions and server-side token refresh.

Key concerns:
- **Data residency:** All data stays on our Hetzner VPS, including auth tokens and user records
- **Cost:** Supabase Cloud free tier has limits; self-hosting has no per-user cost
- **Coupling:** Using Supabase client libraries creates coupling, but only at the infrastructure layer
- **Operational overhead:** Self-hosting means managing GoTrue and Kong containers

## Decision

Self-host Supabase Auth using GoTrue (v2.170.0) behind Kong (3.4) as an API gateway.

- GoTrue handles signup, login, token issuance, and email confirmation
- Kong routes `/auth/v1/*` requests to GoTrue and adds CORS headers
- The backend validates JWTs using the shared `SUPABASE_JWT_SECRET` (HS256)
- The frontend uses `@supabase/ssr` for cookie-based session management

## Consequences

**Easier:**
- Full control over auth configuration and data
- No vendor billing surprises as user count grows
- Auth service runs on the same network as the database — low latency
- Can customize email templates and SMTP settings directly

**More difficult:**
- Must manage GoTrue + Kong containers (version upgrades, monitoring)
- Need to configure SMTP for email confirmation in production
- Debugging auth issues requires understanding GoTrue internals
- Kong declarative config (`infra/kong.yml`) must be maintained manually
