-- Migration 001: Create webhooks table
-- Run this in the Supabase SQL editor or via the Supabase CLI.

CREATE TABLE IF NOT EXISTS webhooks (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             uuid REFERENCES profiles(id) ON DELETE CASCADE,
    merchant_account    text NOT NULL,
    event_code          text NOT NULL,
    psp_reference       text,
    merchant_reference  text,
    amount_value        bigint,
    amount_currency     text,
    success             boolean,
    live                boolean NOT NULL DEFAULT false,
    payload             jsonb NOT NULL DEFAULT '{}',
    received_at         timestamptz NOT NULL DEFAULT now(),
    expires_at          timestamptz NOT NULL
);

-- Index for per-user dashboard queries (newest first)
CREATE INDEX IF NOT EXISTS webhooks_user_received_idx
    ON webhooks (user_id, received_at DESC);

-- Index for efficient cleanup of expired rows
CREATE INDEX IF NOT EXISTS webhooks_expires_at_idx
    ON webhooks (expires_at);

-- Optional: enable Row Level Security so Supabase anon/authenticated keys
-- cannot read other users' webhooks. The backend uses the service role key
-- and bypasses RLS, but this protects direct client access.
ALTER TABLE webhooks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own webhooks"
    ON webhooks FOR SELECT
    USING (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- Automated cleanup with pg_cron (optional but recommended)
-- ---------------------------------------------------------------------------
-- Enable the pg_cron extension in: Supabase Dashboard → Database → Extensions → pg_cron
-- The block below is safe to run whether or not the extension is enabled:
-- if pg_cron is missing it logs a NOTICE and continues without error.
DO $$
BEGIN
    PERFORM cron.schedule(
        'cleanup-expired-webhooks',
        '0 3 * * *',   -- daily at 03:00 UTC
        $cmd$ DELETE FROM webhooks WHERE expires_at < now(); $cmd$
    );
    RAISE NOTICE 'pg_cron job "cleanup-expired-webhooks" scheduled successfully';
EXCEPTION
    WHEN undefined_schema OR undefined_function THEN
        RAISE NOTICE 'pg_cron not enabled — skipping cleanup schedule (enable it in Supabase Dashboard → Database → Extensions)';
END;
$$;

-- To verify once pg_cron is enabled:
-- SELECT * FROM cron.job;
