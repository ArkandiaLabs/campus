.PHONY: lint typecheck test check dev build db-init db-baseline db-migrate db-seed db-psql

# Run psql inside the db container (no local psql required)
DBEXEC = docker compose exec -T db psql -U postgres

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
	$(DBEXEC) < database/schema/baseline.sql

db-migrate:
	$(DBEXEC) < database/migrations/001_add_auth_user_id_to_core_client.sql
	$(DBEXEC) < database/migrations/002_create_ed_content.sql
	$(DBEXEC) < database/migrations/003_create_ed_content_progress.sql
	$(DBEXEC) < database/migrations/004_enable_rls_campus.sql

db-seed:
	$(DBEXEC) < database/seeds/seed.sql

db-psql:
	docker compose exec db psql -U postgres
