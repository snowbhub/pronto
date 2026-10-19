CREATE TABLE IF NOT EXISTS booking_staff_invites (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  staff_id uuid NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
  token_hash text NOT NULL UNIQUE CHECK (token_hash ~ '^[0-9a-f]{64}$'),
  created_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  used_at timestamptz,
  used_by_username text,
  revoked_at timestamptz,
  CHECK ((used_at IS NULL) = (used_by_username IS NULL))
);

CREATE INDEX IF NOT EXISTS booking_staff_invites_staff_created_idx
  ON booking_staff_invites (staff_id, created_at DESC);

ALTER TABLE booking_staff_invites ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE booking_staff_invites FROM PUBLIC, anon, authenticated;
