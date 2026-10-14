-- Inventory ledger. Never allow a negative quantity or delete financial history.
create table if not exists public.booking_product_categories (
 id uuid primary key default gen_random_uuid(),
 name text not null unique check (char_length(trim(name)) between 2 and 90),
 active boolean not null default true
);
create table if not exists public.booking_products (
 id uuid primary key default gen_random_uuid(),
 category_id uuid references public.booking_product_categories(id) on delete set null,
 sku text unique,
 name text not null check (char_length(trim(name)) between 2 and 120),
 sell_price integer not null default 0 check (sell_price>=0),
 purchase_price integer not null default 0 check (purchase_price>=0),
 reorder_level integer not null default 0 check (reorder_level>=0),
 active boolean not null default true,
 created_at timestamptz not null default now()
);
create table if not exists public.booking_stock_movements (
 id uuid primary key default gen_random_uuid(),
 product_id uuid not null references public.booking_products(id) on delete restrict,
 quantity_delta integer not null check(quantity_delta<>0),
 reason text not null check(reason in ('receipt','sale','writeoff','return','adjustment')),
 unit_cost integer check(unit_cost is null or unit_cost>=0),
 note text,
 created_at timestamptz not null default now()
);
create index if not exists booking_stock_moves_product_date on public.booking_stock_movements(product_id,created_at desc);
create or replace view public.booking_stock_balances as
 select p.id as product_id,p.name,p.sku,p.sell_price,p.reorder_level,p.active,
 coalesce(sum(m.quantity_delta),0)::integer as quantity
 from public.booking_products p left join public.booking_stock_movements m on m.product_id=p.id
 group by p.id;
alter table public.booking_product_categories enable row level security;
alter table public.booking_products enable row level security;
alter table public.booking_stock_movements enable row level security;
-- No client RLS policies: management only via server actions behind panel session.
