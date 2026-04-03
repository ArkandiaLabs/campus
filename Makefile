.PHONY: lint typecheck test check dev build db-init db-baseline db-migrate db-seed db-psql

# Database URL for host-side psql (uses mapped port on localhost)
DB_URL ?= postgresql://postgres:$(POSTGRES_PASSWORD)@localhost:5432/postgres

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
	@echo "Waiting for Postgres..."
	@until docker compose exec db pg_isready -U postgres > /dev/null 2>&1; do sleep 1; done
	@echo "Waiting for GoTrue to finish migrations..."
	@sleep 5
	psql "$(DB_URL)" -f database/schema/baseline.sql

db-migrate:
	psql "$(DB_URL)" -f database/migrations/001_add_auth_user_id_to_core_client.sql
	psql "$(DB_URL)" -f database/migrations/002_create_ed_content.sql
	psql "$(DB_URL)" -f database/migrations/003_create_ed_content_progress.sql
	psql "$(DB_URL)" -f database/migrations/004_enable_rls_campus.sql

db-seed:
	psql "$(DB_URL)" -f database/seeds/seed.sql

db-psql:
	psql "$(DB_URL)"
