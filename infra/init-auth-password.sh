#!/bin/bash
# Set supabase_auth_admin password to match POSTGRES_PASSWORD.
# The supabase/postgres image creates this role with a random password,
# but GoTrue connects using POSTGRES_PASSWORD, so they must match.
psql -U supabase_admin -d postgres -c "ALTER ROLE supabase_auth_admin WITH PASSWORD '${POSTGRES_PASSWORD}';"
