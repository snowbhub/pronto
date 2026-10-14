CREATE TABLE IF NOT EXISTS public.booking_checkins (
  appointment_id uuid PRIMARY KEY REFERENCES public.appointments(id) ON DELETE CASCADE,
  arrived_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.booking_checkins ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS booking_checkins_arrived_at_idx ON public.booking_checkins(arrived_at);
