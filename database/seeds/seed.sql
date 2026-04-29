-- ─── Seed: Campus dev data ────────────────────────────────────────────────────
--
-- Creates a complete data chain for local development:
--   offering → cohort → content items
--   client → purchase (completed) → linked to offering + cohort
--   participant → linked to client + cohort + purchase
--
-- After running, register/login via the app and then link your auth user:
--   UPDATE core_client SET auth_user_id = '<id from auth.users>'
--   WHERE email = 'manuel@arkandia.co';
-- ─────────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
    v_offering_id    uuid;
    v_cohort_id      uuid;
    v_session_1_id   uuid;
    v_session_2_id   uuid;
    v_session_3_id   uuid;
    v_session_4_id   uuid;
    v_session_5_id   uuid;
    v_client_id_1    uuid;
    v_purchase_id_1  uuid;
    v_client_id_2    uuid;
    v_purchase_id_2  uuid;
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

-- Content: clear existing to support idempotent re-seeding with new structure
DELETE FROM ed_content WHERE cohort_id = v_cohort_id;
DELETE FROM ed_session WHERE cohort_id = v_cohort_id;

-- Sessions (Tuesdays of April–May 2026, 23:00 UTC = 18:00 COT)
INSERT INTO ed_session (cohort_id, title, scheduled_at, duration_minutes)
VALUES (v_cohort_id, 'Sesión 1: Instrumentando el repositorio', '2026-04-07 23:00:00+00', 120)
RETURNING id INTO v_session_1_id;

INSERT INTO ed_session (cohort_id, title, scheduled_at, duration_minutes)
VALUES (v_cohort_id, 'Sesión 2: Diseño de agentes con LLMs', '2026-04-14 23:00:00+00', 120)
RETURNING id INTO v_session_2_id;

INSERT INTO ed_session (cohort_id, title, scheduled_at, duration_minutes)
VALUES (v_cohort_id, 'Sesión 3: Evaluación y feedback loops', '2026-04-21 23:00:00+00', 120)
RETURNING id INTO v_session_3_id;

INSERT INTO ed_session (cohort_id, title, scheduled_at, duration_minutes)
VALUES (v_cohort_id, 'Sesión 4: Patrones avanzados de prompting', '2026-04-28 23:00:00+00', 120)
RETURNING id INTO v_session_4_id;

INSERT INTO ed_session (cohort_id, title, scheduled_at, duration_minutes)
VALUES (v_cohort_id, 'Sesión 5: Deploy y operaciones', '2026-05-05 23:00:00+00', 120)
RETURNING id INTO v_session_5_id;

-- Content: 1 video per session + 2 general downloads (session_id IS NULL)
INSERT INTO ed_content (cohort_id, session_id, title, content_type, content_url, position, is_preview)
VALUES
    (v_cohort_id, v_session_1_id, 'Grabación de la Sesión', 'video',    'https://vimeo.com/100000001',                1, true),
    (v_cohort_id, v_session_2_id, 'Grabación de la Sesión', 'video',    'https://vimeo.com/100000002',                2, false),
    (v_cohort_id, v_session_3_id, 'Grabación de la Sesión', 'video',    'https://vimeo.com/100000003',                3, false),
    (v_cohort_id, v_session_4_id, 'Grabación de la Sesión', 'video',    'https://vimeo.com/100000004',                4, false),
    (v_cohort_id, v_session_5_id, 'Grabación de la Sesión', 'video',    'https://vimeo.com/100000005',                5, false),
    (v_cohort_id, NULL,           'Kit de configuración',   'download', 'https://storage.placeholder.co/kit.zip',     6, false),
    (v_cohort_id, NULL,           'Guía de prompts',        'download', 'https://storage.placeholder.co/guia.pdf',    7, false);

-- Client 1: Manuel
INSERT INTO core_client (email, first_name, last_name)
VALUES ('manuel@arkandia.co', 'Manuel', 'Zapata')
ON CONFLICT (email) DO NOTHING
RETURNING id INTO v_client_id_1;

IF v_client_id_1 IS NULL THEN
    SELECT id INTO v_client_id_1 FROM core_client WHERE email = 'manuel@arkandia.co';
END IF;

-- Purchase 1
INSERT INTO core_purchase (client_id, offering_id, cohort_id, amount_paid, currency, status, purchased_at)
VALUES (v_client_id_1, v_offering_id, v_cohort_id, 0, 'USD', 'completed', now())
ON CONFLICT DO NOTHING
RETURNING id INTO v_purchase_id_1;

IF v_purchase_id_1 IS NULL THEN
    SELECT id INTO v_purchase_id_1 FROM core_purchase WHERE client_id = v_client_id_1 AND offering_id = v_offering_id LIMIT 1;
END IF;

-- Participant 1
INSERT INTO ed_participant (cohort_id, client_id, purchase_id, email, first_name, last_name)
VALUES (v_cohort_id, v_client_id_1, v_purchase_id_1, 'manuel@arkandia.co', 'Manuel', 'Zapata')
ON CONFLICT DO NOTHING;

-- Client 2: David
INSERT INTO core_client (email, first_name, last_name)
VALUES ('david@arkandia.co', 'David', 'Arkandia')
ON CONFLICT (email) DO NOTHING
RETURNING id INTO v_client_id_2;

IF v_client_id_2 IS NULL THEN
    SELECT id INTO v_client_id_2 FROM core_client WHERE email = 'david@arkandia.co';
END IF;

-- Purchase 2
INSERT INTO core_purchase (client_id, offering_id, cohort_id, amount_paid, currency, status, purchased_at)
VALUES (v_client_id_2, v_offering_id, v_cohort_id, 0, 'USD', 'completed', now())
ON CONFLICT DO NOTHING
RETURNING id INTO v_purchase_id_2;

IF v_purchase_id_2 IS NULL THEN
    SELECT id INTO v_purchase_id_2 FROM core_purchase WHERE client_id = v_client_id_2 AND offering_id = v_offering_id LIMIT 1;
END IF;

-- Participant 2
INSERT INTO ed_participant (cohort_id, client_id, purchase_id, email, first_name, last_name)
VALUES (v_cohort_id, v_client_id_2, v_purchase_id_2, 'david@arkandia.co', 'David', 'Arkandia')
ON CONFLICT DO NOTHING;

RAISE NOTICE 'Seeded offering=% cohort=% clients=[%, %]', v_offering_id, v_cohort_id, v_client_id_1, v_client_id_2;

END $$;
