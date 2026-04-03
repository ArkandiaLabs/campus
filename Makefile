.PHONY: lint typecheck test check dev build db-init db-migrate db-seed

lint:
	cd backend && uv run ruff check app tests
	cd backend && uv run ruff format --check app tests
	cd frontend && pnpm eslint src

typecheck:
	cd backend && uv run pyright
	cd frontend && pnpm tsc --noEmit

test:
	cd backend && uv run pytest
	cd frontend && pnpm vitest run

check: lint typecheck test

dev:
	docker compose up

build:
	docker compose build

db-init: db-baseline db-migrate

db-baseline:
	psql $(DATABASE_URL) -f database/schema/baseline.sql

db-migrate:
	psql $(DATABASE_URL) -f database/migrations/001_add_auth_user_id_to_core_client.sql
	psql $(DATABASE_URL) -f database/migrations/002_create_ed_content.sql
	psql $(DATABASE_URL) -f database/migrations/003_create_ed_content_progress.sql
	psql $(DATABASE_URL) -f database/migrations/004_enable_rls_campus.sql

db-seed:
	psql $(DATABASE_URL) -f database/seeds/seed.sql
