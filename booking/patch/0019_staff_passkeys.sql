CREATE TABLE IF NOT EXISTS booking_staff_passkeys (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  staff_id uuid NOT NULL REFERENCES booking_staff_accounts(staff_id) ON DELETE CASCADE,
  credential_id text NOT NULL UNIQUE,
  public_key bytea NOT NULL,
  sign_count bigint NOT NULL DEFAULT 0,
  transports text[] NOT NULL DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(),
  last_used_at timestamptz
);
ALTER TABLE booking_staff_accounts ADD COLUMN IF NOT EXISTS webauthn_challenge text;
ALTER TABLE booking_staff_accounts ADD COLUMN IF NOT EXISTS webauthn_challenge_expires_at timestamptz;
CREATE INDEX IF NOT EXISTS booking_staff_passkeys_staff_idx ON booking_staff_passkeys(staff_id);
ALTER TABLE booking_staff_passkeys ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE booking_staff_passkeys FROM PUBLIC, anon, authenticated;
