-- 10_memories.sql
-- Requires: 00_extensions.sql

create table if not exists public.memories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  description text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_memories_updated_at on public.memories;
create trigger trg_memories_updated_at
before update on public.memories
for each row
execute function public.set_updated_at();

create index if not exists idx_memories_user on public.memories(user_id);

alter table public.memories enable row level security;

create policy if not exists "memories select own" on public.memories
for select using (auth.uid() = user_id);

create policy if not exists "memories insert own" on public.memories
for insert with check (auth.uid() = user_id);

create policy if not exists "memories update own" on public.memories
for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy if not exists "memories delete own" on public.memories
for delete using (auth.uid() = user_id);

-- No URLs to paste here. Auth keys are configured at project level.
