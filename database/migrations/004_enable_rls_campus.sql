-- Migration 004: Enable RLS for Campus tables

-- ─── ed_content ───────────────────────────────────────────────────────────────

ALTER TABLE public.ed_content ENABLE ROW LEVEL SECURITY;

-- Anyone (authenticated or anon) can read content from published/active/completed cohorts.
CREATE POLICY "ed_content_select_published"
    ON public.ed_content
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.ed_cohort ec
            WHERE ec.id = ed_content.cohort_id
              AND ec.status IN ('published', 'active', 'completed')
        )
    );

-- All write operations require service_role (bypasses RLS).

-- ─── ed_content_progress ──────────────────────────────────────────────────────

ALTER TABLE public.ed_content_progress ENABLE ROW LEVEL SECURITY;

-- Users can read their own progress.
CREATE POLICY "ed_content_progress_select_own"
    ON public.ed_content_progress
    FOR SELECT
    USING (user_id = auth.uid());

-- Users can insert their own progress.
CREATE POLICY "ed_content_progress_insert_own"
    ON public.ed_content_progress
    FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- Users can delete their own progress.
CREATE POLICY "ed_content_progress_delete_own"
    ON public.ed_content_progress
    FOR DELETE
    USING (user_id = auth.uid());

-- UPDATE requires service_role (bypasses RLS).
