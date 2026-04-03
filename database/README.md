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

## Setup

The self-hosted `supabase/postgres` image and GoTrue automatically create the `auth` schema and `auth.users` table. Start the services first, then initialize the database:

```bash
# Terminal 1: start all services (Postgres, GoTrue, Kong, backend, frontend)
make dev

# Terminal 2: wait for GoTrue to finish its migrations, then init
make db-init    # runs baseline + migrations
make db-seed    # optional: sample content (edit cohort_id first)
```

### Production (tables already exist)

Only run the campus migrations:

```bash
make db-migrate
```

## Migrations

| File | Description |
|------|-------------|
| `001_add_auth_user_id_to_core_client.sql` | Adds `auth_user_id` column to link auth users to client records |
| `002_create_ed_content.sql` | Creates `ed_content` table for workshop videos, downloads, and links |
| `003_create_ed_content_progress.sql` | Creates `ed_content_progress` table for tracking user completion |
| `004_enable_rls_campus.sql` | Enables Row Level Security on the new tables |

Apply migrations in order — they have dependencies.

## Seeds

`seeds/seed.sql` populates `ed_content` with sample workshop content for a dev cohort.

**Before running:**
1. Open `seeds/seed.sql` and replace `PLACEHOLDER_COHORT_ID` with a real cohort UUID:
   ```sql
   make db-psql
   SELECT id, title FROM ed_cohort;
   ```
2. Update the cohort ID in the seed file.

**Run:**
```bash
make db-seed
```

## Linking Auth Users to Clients

After a user registers via Campus, link their auth user to their `core_client` record:

```sql
make db-psql
UPDATE core_client SET auth_user_id = '<uuid from auth.users>' WHERE email = '<user email>';
```

Without this, the user will authenticate successfully but see an empty catalog.
