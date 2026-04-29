-- Migration 006: Add description to ed_session and link ed_content to ed_session
-- ed_session.description: optional text description for the recorded session.
-- ed_content.session_id: nullable FK — content belonging to a session vs general cohort resource (NULL).

ALTER TABLE public.ed_session ADD COLUMN description text;

ALTER TABLE public.ed_content
    ADD COLUMN session_id uuid REFERENCES public.ed_session(id) ON DELETE SET NULL;

CREATE INDEX idx_ed_content_session_id ON public.ed_content(session_id);
