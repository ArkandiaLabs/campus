-- ─── Seed: Campus dev data ────────────────────────────────────────────────────
--
-- Creates a complete data chain for local development:
--   offering → cohort → content items
--   client (linked to auth user) → purchase
--
-- After running, register/login via the app and then link your auth user:
--   UPDATE core_client SET auth_user_id = '<id from auth.users>'
--   WHERE email = '<your email>';
-- ─────────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
    v_offering_id uuid;
    v_cohort_id   uuid;
BEGIN

-- Offering
INSERT INTO core_offering (title, type)
VALUES ('Workshop: AI Engineering', 'workshop')
ON CONFLICT DO NOTHING
RETURNING id INTO v_offering_id;

IF v_offering_id IS NULL THEN
    SELECT id INTO v_offering_id FROM core_offering WHERE title = 'Workshop: AI Engineering';
END IF;

-- Cohort
INSERT INTO ed_cohort (offering_id, title)
VALUES (v_offering_id, 'Cohorte Abril 2026')
ON CONFLICT DO NOTHING
RETURNING id INTO v_cohort_id;

IF v_cohort_id IS NULL THEN
    SELECT id INTO v_cohort_id FROM ed_cohort WHERE offering_id = v_offering_id LIMIT 1;
END IF;

-- Content
INSERT INTO ed_content (cohort_id, title, content_type, content_url, position, is_preview)
VALUES
    (v_cohort_id, 'Sesion 1: Instrumentando el repositorio',   'video',    'https://vimeo.com/placeholder/sesion-1', 1, true),
    (v_cohort_id, 'Sesion 2: Diseño de agentes con LLMs',      'video',    'https://vimeo.com/placeholder/sesion-2', 2, false),
    (v_cohort_id, 'Sesion 3: Evaluacion y feedback loops',     'video',    'https://vimeo.com/placeholder/sesion-3', 3, false),
    (v_cohort_id, 'Sesion 4: Patrones avanzados de prompting', 'video',    'https://vimeo.com/placeholder/sesion-4', 4, false),
    (v_cohort_id, 'Sesion 5: Deploy y operaciones',            'video',    'https://vimeo.com/placeholder/sesion-5', 5, false),
    (v_cohort_id, 'Kit de configuracion',                      'download', 'https://storage.placeholder.co/kit.zip', 6, false),
    (v_cohort_id, 'Guia de prompts',                           'download', 'https://storage.placeholder.co/guia.pdf', 7, false)
ON CONFLICT DO NOTHING;

RAISE NOTICE 'Seeded offering=% cohort=%', v_offering_id, v_cohort_id;

END $$;
