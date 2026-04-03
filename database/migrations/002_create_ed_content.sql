-- Migration 002: Create ed_content table
-- Stores content items (videos, downloads, links) belonging to a cohort.

CREATE TABLE public.ed_content (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    cohort_id uuid NOT NULL REFERENCES public.ed_cohort(id) ON DELETE CASCADE,
    title text NOT NULL,
    description text,
    content_type text NOT NULL CHECK (content_type IN ('video', 'download', 'link')),
    content_url text NOT NULL,
    position integer NOT NULL,
    is_preview boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_ed_content_cohort_id ON public.ed_content(cohort_id);
CREATE INDEX idx_ed_content_position ON public.ed_content(cohort_id, position);
