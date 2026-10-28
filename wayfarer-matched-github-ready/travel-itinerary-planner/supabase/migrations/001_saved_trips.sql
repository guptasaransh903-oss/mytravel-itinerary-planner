-- WanderPlan: saved trips table
-- Run this in the Supabase SQL Editor (Dashboard → SQL → New query).
-- Keeps Row Level Security ENABLED. Do not turn RLS off.
--
-- Auth status: user authentication is NOT implemented yet.
-- Safe approach for now:
--   1. Frontend never talks to Supabase directly and never receives the service-role key.
--   2. FastAPI uses SUPABASE_SERVICE_ROLE_KEY (server-only) to read/write rows.
--      The service role bypasses RLS by design; RLS still blocks anon/authenticated
--      clients that hit Supabase directly.
--   3. Each browser sends X-WanderPlan-Owner-Key (a local UUID). The API scopes
--      all queries to that owner_key so devices do not share trips by accident.
-- When you add Supabase Auth later:
--   - Set user_id = auth.uid() on insert
--   - Replace owner_key scoping with auth.uid() = user_id policies
--   - Stop using the service role for user-scoped CRUD if you prefer user JWTs

create extension if not exists "pgcrypto";

create table if not exists public.saved_trips (
  id uuid primary key default gen_random_uuid(),
  owner_key text not null,
  user_id uuid null references auth.users (id) on delete set null,
  destination text not null,
  start_date date not null,
  end_date date not null,
  budget_inr integer not null check (budget_inr > 0),
  travel_style text not null check (travel_style in ('relaxed', 'balanced', 'adventurous')),
  interests jsonb not null default '[]'::jsonb,
  preferences jsonb not null default '{}'::jsonb,
  itinerary jsonb not null,
  total_estimated_cost_inr integer not null default 0,
  trip_days integer not null default 1,
  title text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint saved_trips_date_range check (end_date >= start_date)
);

create index if not exists saved_trips_owner_key_idx on public.saved_trips (owner_key);
create index if not exists saved_trips_user_id_idx on public.saved_trips (user_id);
create index if not exists saved_trips_created_at_idx on public.saved_trips (created_at desc);

create or replace function public.set_saved_trips_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_saved_trips_updated_at on public.saved_trips;
create trigger trg_saved_trips_updated_at
before update on public.saved_trips
for each row
execute function public.set_saved_trips_updated_at();

alter table public.saved_trips enable row level security;

-- Revoke direct table access from anon/authenticated browser clients.
-- Backend service role still works (bypasses RLS).
revoke all on table public.saved_trips from anon, authenticated;

-- Future Auth-ready policies (inactive until you start setting user_id from JWTs).
-- Uncomment after Supabase Auth is wired and you insert with user_id = auth.uid().
--
-- create policy "Users can select own trips"
--   on public.saved_trips for select to authenticated
--   using (auth.uid() = user_id);
--
-- create policy "Users can insert own trips"
--   on public.saved_trips for insert to authenticated
--   with check (auth.uid() = user_id);
--
-- create policy "Users can update own trips"
--   on public.saved_trips for update to authenticated
--   using (auth.uid() = user_id)
--   with check (auth.uid() = user_id);
--
-- create policy "Users can delete own trips"
--   on public.saved_trips for delete to authenticated
--   using (auth.uid() = user_id);
