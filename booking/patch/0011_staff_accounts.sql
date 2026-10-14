-- Booking: separate staff credentials. Passwords are scrypt-hashed by the server.
-- Public Supabase client access is disabled; all reads/writes use server + panel/staff guard.
create table if not exists public.booking_staff_accounts (
 staff_id uuid primary key references public.staff(id) on delete cascade,
 username text not null unique check(username ~ '^[a-z0-9._-]{3,40}$'),
 password_hash text not null,
 active boolean not null default true,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
alter table public.booking_staff_accounts enable row level security;
create index if not exists booking_staff_accounts_active on public.booking_staff_accounts(active);
