-- Migration 003: Allow multiple saved Adyen accounts per user with a
-- server-side "active account" pointer on the profiles table.
--
-- Before: adyen_configs had UNIQUE(user_id) — one config per user.
-- After:  a user may have many adyen_configs rows (one per company account);
--         profiles.active_adyen_config_id selects which one is active.
--
-- Switching the active account updates only profiles (a single row), so it
-- never triggers the locked-row BEFORE UPDATE guard on adyen_configs and needs
-- no atomic multi-row swap. The locked trigger still blocks credential edits.

-- 1. A human-friendly name for each saved account.
ALTER TABLE public.adyen_configs
    ADD COLUMN IF NOT EXISTS label text NOT NULL DEFAULT '';

-- 2. Drop the one-row-per-user constraint so multiple accounts are allowed.
--    (Default constraint name for a UNIQUE(user_id) column is
--    adyen_configs_user_id_key.)
ALTER TABLE public.adyen_configs
    DROP CONSTRAINT IF EXISTS adyen_configs_user_id_key;

-- 3. Index to keep per-user account lookups fast.
CREATE INDEX IF NOT EXISTS adyen_configs_user_id_idx
    ON public.adyen_configs (user_id);

-- 4. The active-account pointer lives on profiles. ON DELETE SET NULL means
--    deleting the active account simply clears the pointer.
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS active_adyen_config_id uuid
    REFERENCES public.adyen_configs(id) ON DELETE SET NULL;

-- 5. Backfill: name existing rows and point each user at their existing config.
UPDATE public.adyen_configs
    SET label = 'Default'
    WHERE label = '';

UPDATE public.profiles p
    SET active_adyen_config_id = c.id
    FROM public.adyen_configs c
    WHERE c.user_id = p.id
      AND p.active_adyen_config_id IS NULL;
