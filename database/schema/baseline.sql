-- ─── Baseline schema ──────────────────────────────────────────────────────────
--
-- Creates the tables that already exist in production. Run this ONCE when
-- bootstrapping a new environment (dev, test, CI), then apply the campus
-- migrations on top.
--
-- DO NOT run this in production — these tables are already there.
-- ─────────────────────────────────────────────────────────────────────────────

-- ─── Enum types ──────────────────────────────────────────────────────────────

CREATE TYPE offering_type AS ENUM (
    'workshop', 'course', 'saas_subscription', 'consulting', 'master_class'
);

CREATE TYPE offering_status AS ENUM (
    'draft', 'published', 'closed', 'archived'
);

CREATE TYPE purchase_status AS ENUM (
    'pending', 'completed', 'refunded', 'failed'
);

CREATE TYPE payment_method AS ENUM (
    'card', 'paypal', 'pse', 'bank_transfer'
);

CREATE TYPE lms_provider AS ENUM (
    'gumroad', 'hotmart', 'cursosmz', 'youtube', 'manual', 'in_person'
);

CREATE TYPE cohort_status AS ENUM (
    'draft', 'published', 'active', 'completed', 'cancelled'
);

CREATE TYPE certificate_status AS ENUM (
    'pending', 'issued', 'failed'
);

-- ─── Reference tables ────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.core_country (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    code text NOT NULL UNIQUE,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.core_company (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    domain text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

-- ─── Core tables ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.core_offering (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title text NOT NULL,
    description text,
    type offering_type NOT NULL,
    status offering_status NOT NULL DEFAULT 'draft',
    category text,
    external_ids jsonb NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.core_client (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text NOT NULL UNIQUE,
    first_name text,
    last_name text,
    phone text,
    title text,
    seniority text,
    city text,
    state text,
    country_id uuid REFERENCES public.core_country(id),
    company_id uuid REFERENCES public.core_company(id),
    linkedin_url text,
    enrichment jsonb NOT NULL DEFAULT '{}',
    enriched_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

-- ─── Education tables ────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.ed_cohort (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    offering_id uuid NOT NULL REFERENCES public.core_offering(id),
    title text NOT NULL,
    start_date date,
    end_date date,
    max_participants integer,
    status cohort_status NOT NULL DEFAULT 'draft',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.core_purchase (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id uuid NOT NULL REFERENCES public.core_client(id),
    offering_id uuid NOT NULL REFERENCES public.core_offering(id),
    cohort_id uuid REFERENCES public.ed_cohort(id),
    external_purchase_id text UNIQUE,
    amount_paid numeric NOT NULL,
    net_amount numeric,
    currency text NOT NULL DEFAULT 'USD',
    status purchase_status NOT NULL DEFAULT 'pending',
    payment_method payment_method,
    lms_provider lms_provider,
    referrer_url text,
    attribution_source text,
    metadata jsonb,
    purchased_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.ed_session (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    cohort_id uuid NOT NULL REFERENCES public.ed_cohort(id),
    title text NOT NULL,
    scheduled_at timestamptz,
    duration_minutes integer,
    zoom_meeting_id text,
    zoom_meeting_url text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.ed_participant (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    cohort_id uuid NOT NULL REFERENCES public.ed_cohort(id),
    client_id uuid REFERENCES public.core_client(id),
    purchase_id uuid REFERENCES public.core_purchase(id),
    email text NOT NULL,
    first_name text,
    last_name text,
    certificate_id text,
    certificate_status certificate_status DEFAULT 'pending',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
