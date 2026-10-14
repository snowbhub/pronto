-- Booking extension 0009: staff professional levels and level-specific services.
-- Does not alter existing appointments, payments, or internal role enums.
create table if not exists public.booking_staff_levels (
 staff_id uuid primary key references public.staff(id) on delete cascade,
 professional_level text not null default 'barber'
   check (professional_level in ('trainee','junior','barber','senior')),
 updated_at timestamptz not null default now()
);
create table if not exists public.booking_service_levels (
 service_id uuid not null references public.services(id) on delete cascade,
 professional_level text not null check (professional_level in ('trainee','junior','barber','senior')),
 available boolean not null default true,
 price_override integer check (price_override is null or price_override>=0),
 duration_override_min integer check (duration_override_min is null or duration_override_min between 5 and 480),
 primary key(service_id,professional_level)
);
create index if not exists booking_service_levels_level_idx on public.booking_service_levels(professional_level);
alter table public.booking_staff_levels enable row level security;
alter table public.booking_service_levels enable row level security;
-- Managed through authenticated server-side functions using the existing panel guard.
