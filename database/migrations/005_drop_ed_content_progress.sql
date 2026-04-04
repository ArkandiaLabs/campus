-- Migration 004: Drop ed_content_progress table
-- Progress tracking is being removed from the application.

DROP TABLE IF EXISTS public.ed_content_progress;
