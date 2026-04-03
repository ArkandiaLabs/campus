-- Migration 001: Add auth_user_id to core_client
-- Bridges Supabase Auth users with existing client records.
-- After a user registers via Campus, set this column manually via:
--   UPDATE core_client SET auth_user_id = '<auth.users.id>' WHERE email = '<email>';

ALTER TABLE public.core_client
ADD COLUMN auth_user_id uuid UNIQUE REFERENCES auth.users(id);

CREATE INDEX idx_core_client_auth_user_id ON public.core_client(auth_user_id);
