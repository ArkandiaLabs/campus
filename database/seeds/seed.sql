-- ─── Seed: Campus content for development ────────────────────────────────────
--
-- BEFORE RUNNING:
--   1. Replace PLACEHOLDER_COHORT_ID below with an actual cohort ID from your
--      dev Supabase instance. Run: SELECT id, title FROM ed_cohort;
--
--   2. After users register via Campus, link their Supabase auth user to their
--      core_client record:
--        UPDATE core_client
--        SET auth_user_id = '<id from auth.users>'
--        WHERE email = '<user email>';
--      Without this step, the user will see an empty catalog.
--
-- ─────────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
    -- Replace with actual cohort ID from dev Supabase:
    --   SELECT id, title FROM ed_cohort;
    v_cohort_id uuid := 'PLACEHOLDER_COHORT_ID'::uuid;
BEGIN

INSERT INTO public.ed_content (cohort_id, title, content_type, content_url, position, is_preview)
VALUES
    (v_cohort_id, 'Sesion 1: Instrumentando el repositorio',  'video',    'https://vimeo.com/placeholder/sesion-1', 1, true),
    (v_cohort_id, 'Sesion 2: Diseño de agentes con LLMs',     'video',    'https://vimeo.com/placeholder/sesion-2', 2, false),
    (v_cohort_id, 'Sesion 3: Evaluacion y feedback loops',    'video',    'https://vimeo.com/placeholder/sesion-3', 3, false),
    (v_cohort_id, 'Sesion 4: Patrones avanzados de prompting','video',    'https://vimeo.com/placeholder/sesion-4', 4, false),
    (v_cohort_id, 'Sesion 5: Deploy y operaciones',           'video',    'https://vimeo.com/placeholder/sesion-5', 5, false),
    (v_cohort_id, 'Kit de configuracion',                     'download', 'https://storage.placeholder.co/kit-configuracion.zip', 6, false),
    (v_cohort_id, 'Guia de prompts',                          'download', 'https://storage.placeholder.co/guia-prompts.pdf',      7, false);

END $$;
