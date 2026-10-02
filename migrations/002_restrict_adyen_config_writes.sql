CREATE TABLE IF NOT EXISTS public.adyen_configs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    api_key text NOT NULL DEFAULT '',
    client_key text NOT NULL DEFAULT '',
    merchant_account text NOT NULL DEFAULT '',
    locked boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.adyen_configs
ADD COLUMN IF NOT EXISTS locked boolean NOT NULL DEFAULT false;

ALTER TABLE public.adyen_configs ENABLE ROW LEVEL SECURITY;
REVOKE ALL PRIVILEGES ON TABLE public.adyen_configs FROM anon, authenticated;

CREATE OR REPLACE FUNCTION public.prevent_locked_adyen_config_update()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.locked THEN
        RAISE EXCEPTION 'This configuration is locked and cannot be modified' USING ERRCODE = '42501';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS prevent_locked_adyen_config_update ON public.adyen_configs;
CREATE TRIGGER prevent_locked_adyen_config_update
BEFORE UPDATE ON public.adyen_configs
FOR EACH ROW
EXECUTE FUNCTION public.prevent_locked_adyen_config_update();
