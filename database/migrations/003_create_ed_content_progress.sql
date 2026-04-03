-- Migration 003: Create ed_content_progress table
-- Tracks which content items each user has completed.

CREATE TABLE public.ed_content_progress (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id),
    content_id uuid NOT NULL REFERENCES public.ed_content(id) ON DELETE CASCADE,
    completed_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (user_id, content_id)
);

CREATE INDEX idx_ed_content_progress_user_id ON public.ed_content_progress(user_id);
CREATE INDEX idx_ed_content_progress_content_id ON public.ed_content_progress(content_id);
