# Database

This directory contains the schema, migrations, and seed data for Arkandia Campus.

## Directory Structure

```
database/
├── schema/
│   └── baseline.sql       # Pre-existing tables (run once for new environments)
├── migrations/            # Campus-specific changes (run in order, every environment)
│   ├── 001_add_auth_user_id_to_core_client.sql
│   ├── 002_create_ed_content.sql
│   ├── 003_create_ed_content_progress.sql
│   └── 004_enable_rls_campus.sql
└── seeds/
    └── seed.sql           # Sample content for dev
```

## Setup by Environment

### New dev/test/CI environment (no existing tables)

Run the baseline first, then all migrations:

```bash
psql $DATABASE_URL -f database/schema/baseline.sql
psql $DATABASE_URL -f database/migrations/001_add_auth_user_id_to_core_client.sql
psql $DATABASE_URL -f database/migrations/002_create_ed_content.sql
psql $DATABASE_URL -f database/migrations/003_create_ed_content_progress.sql
psql $DATABASE_URL -f database/migrations/004_enable_rls_campus.sql
```

> **Note:** `baseline.sql` does NOT reference `auth.users` (Supabase Auth). Migration 001 adds a FK to `auth.users` and migration 003 creates a FK to `auth.users`. If you're running against a plain Postgres (not Supabase), you'll need to create the `auth` schema and `auth.users` table yourself, or comment out those FKs.

### Production (tables already exist)

Only run the migrations — never run `baseline.sql`:

```bash
psql $DATABASE_URL -f database/migrations/001_add_auth_user_id_to_core_client.sql
psql $DATABASE_URL -f database/migrations/002_create_ed_content.sql
psql $DATABASE_URL -f database/migrations/003_create_ed_content_progress.sql
psql $DATABASE_URL -f database/migrations/004_enable_rls_campus.sql
```

## Migrations

| File | Description |
|------|-------------|
| `001_add_auth_user_id_to_core_client.sql` | Adds `auth_user_id` column to link Supabase Auth users to client records |
| `002_create_ed_content.sql` | Creates `ed_content` table for workshop videos, downloads, and links |
| `003_create_ed_content_progress.sql` | Creates `ed_content_progress` table for tracking user completion |
| `004_enable_rls_campus.sql` | Enables Row Level Security on the new tables |

Apply migrations in order — they have dependencies.

## Seeds

`seeds/seed.sql` populates `ed_content` with sample workshop content for a dev cohort.

**Before running:**
1. Open `seeds/seed.sql` and replace `PLACEHOLDER_COHORT_ID` with a real cohort UUID:
   ```sql
   SELECT id, title FROM ed_cohort;
   ```
2. Update the cohort ID in the seed file.

**Run:**
```bash
psql $DATABASE_URL -f database/seeds/seed.sql
```

## Linking Auth Users to Clients

After a user registers via Campus, link their Supabase Auth user to their `core_client` record:

```sql
UPDATE core_client
SET auth_user_id = '<uuid from auth.users>'
WHERE email = '<user email>';
```

Without this, the user will authenticate successfully but see an empty catalog.
