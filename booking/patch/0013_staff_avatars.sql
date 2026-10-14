create table if not exists public.booking_staff_avatars (
 staff_id uuid primary key references public.staff(id) on delete cascade,
 mime_type text not null check (mime_type in ('image/jpeg','image/png','image/webp')),
 image_data bytea not null check (octet_length(image_data) between 1 and 350000),
 updated_at timestamptz not null default now()
);
alter table public.booking_staff_avatars enable row level security;