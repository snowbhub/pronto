create table if not exists public.booking_expense_types(
 id uuid primary key default gen_random_uuid(),
 name text not null unique check(char_length(trim(name)) between 2 and 90),
 active boolean not null default true
);
create table if not exists public.booking_expense_details(
 expense_id uuid primary key references public.expenses(id) on delete cascade,
 expense_type_id uuid references public.booking_expense_types(id) on delete set null,
 payee text,
 created_at timestamptz not null default now()
);
create table if not exists public.booking_cash_movements(
 id uuid primary key default gen_random_uuid(),
 direction text not null check(direction in ('deposit','withdrawal')),
 amount integer not null check(amount>0),
 recipient text,
 note text,
 created_at timestamptz not null default now()
);
create index if not exists booking_cash_movements_date_idx on public.booking_cash_movements(created_at desc);
alter table public.booking_expense_types enable row level security;
alter table public.booking_expense_details enable row level security;
alter table public.booking_cash_movements enable row level security;
-- No direct anon/authenticated database policies: authorized server actions only.
