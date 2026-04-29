.PHONY: dev build db-init db-baseline db-migrate db-seed db-psql \
       lint lint-backend lint-frontend \
       typecheck typecheck-backend typecheck-frontend \
       test test-backend test-frontend \
       check fmt audit audit-backend audit-frontend \
       arch arch-backend hooks \
	   tokens design-lint design-check

# Run psql inside the db container (no local psql required)
DBEXEC = docker compose exec -T db psql -U postgres

dev:
	docker compose up

build:
	docker compose build

db-init: db-baseline db-migrate

db-baseline:
	@echo "Waiting for Postgres..."
	@until docker compose exec db pg_isready -U postgres > /dev/null 2>&1; do sleep 1; done
	@echo "Waiting for GoTrue to finish migrations..."
	@sleep 5
	$(DBEXEC) < database/schema/baseline.sql

db-migrate:
	$(DBEXEC) < database/migrations/001_add_auth_user_id_to_core_client.sql
	$(DBEXEC) < database/migrations/002_create_ed_content.sql
	$(DBEXEC) < database/migrations/003_create_ed_content_progress.sql
	$(DBEXEC) < database/migrations/004_enable_rls_campus.sql
	$(DBEXEC) < database/migrations/005_drop_ed_content_progress.sql
	$(DBEXEC) < database/migrations/006_sessions_content_link.sql

db-seed:
	$(DBEXEC) < database/seeds/seed.sql

db-psql:
	docker compose exec db psql -U postgres

# ─── Lint ────────────────────────────────────────────────────────────────────

lint: lint-backend lint-frontend

lint-backend:
	cd backend && uv run ruff check app tests

lint-frontend:
	cd frontend && pnpm run lint

# ─── Type check ──────────────────────────────────────────────────────────────

typecheck: typecheck-backend typecheck-frontend

typecheck-backend:
	cd backend && uv run pyright

typecheck-frontend:
	cd frontend && pnpm run typecheck

# ─── Design system ───────────────────────────────────────────────────────────

tokens:
	cd frontend && pnpm design:tokens

design-lint:
	cd frontend && pnpm design:lint

design-check:
	cd frontend && pnpm design:check

# ─── Test ────────────────────────────────────────────────────────────────────

test: test-backend test-frontend

test-backend:
	cd backend && uv run pytest -v

test-frontend:
	cd frontend && pnpm run test

# ─── All checks ──────────────────────────────────────────────────────────────

check: lint typecheck test design-lint

# ─── Format (auto-fix) ──────────────────────────────────────────────────────

fmt:
	cd backend && uv run ruff check --fix app tests && uv run ruff format app tests
	cd frontend && pnpm eslint --fix src

# ─── Dependency audit ────────────────────────────────────────────────────────

audit: audit-backend audit-frontend

audit-backend:
	cd backend && uv audit

audit-frontend:
	cd frontend && pnpm audit

# ─── Architecture ────────────────────────────────────────────────────────────

arch: arch-backend

arch-backend:
	cd backend && uv run lint-imports

# ─── Git hooks ───────────────────────────────────────────────────────────────

hooks:
	lefthook install
