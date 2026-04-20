# ADR-003: Single-Server Docker Compose Deployment

## Status

Accepted

## Context

Campus needs to be deployed to production. Options considered:

1. **Cloud PaaS** (Vercel + Railway/Render) — managed, zero-ops, but split infrastructure and higher cost at scale
2. **Kubernetes** — full orchestration, overkill for a solo-developer project
3. **Single VPS + Docker Compose** — all services on one server, simple and cheap
4. **Serverless** — Lambda/Cloud Functions — doesn't fit the self-hosted Supabase requirement

Campus runs 6 containers: PostgreSQL, GoTrue, Kong, Backend, Frontend, Caddy. The expected load is low (hundreds of users, not thousands). The team is small.

Key concerns:
- **Cost:** A Hetzner VPS is ~$5-20/month vs $50+/month for managed services
- **Complexity:** One `docker compose up` vs managing multiple cloud services
- **Reliability:** Single point of failure, but acceptable for the current scale
- **Scaling:** Vertical scaling (bigger VPS) is sufficient for the foreseeable future

## Decision

Deploy all services to a single Hetzner VPS using Docker Compose.

- `infra/docker-compose.prod.yml` defines all 6 services
- Caddy handles TLS termination with automatic Let's Encrypt certificates
- CI/CD via GitHub Actions: push to `main` → SSH → `git pull` → `docker compose build` → `docker compose up -d`
- All services on a single Docker bridge network (`campus_network`)
- Only ports 80 and 443 are exposed to the internet

## Consequences

**Easier:**
- One command deploys everything
- All logs in one place (`docker compose logs`)
- No cloud vendor lock-in
- Low monthly cost (~$5-20/month for the VPS)
- Full control over the environment

**More difficult:**
- Single point of failure — if the VPS goes down, everything goes down
- No horizontal scaling without re-architecting
- Manual server setup required (one-time, via `infra/setup-server.sh`)
- No zero-downtime deploys — containers restart during deployment
- Backups must be configured manually (database volumes)
