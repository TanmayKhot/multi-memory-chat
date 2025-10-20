-- 20_memory_records.sql
-- Requires: 10_memories.sql

create table if not exists public.memory_records (
  id uuid primary key default gen_random_uuid(),
  memory_id uuid not null references public.memories(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  content text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_records_memory on public.memory_records(memory_id);
create index if not exists idx_records_user on public.memory_records(user_id);

alter table public.memory_records enable row level security;

create policy if not exists "records select by owner" on public.memory_records
for select using (
  auth.uid() = user_id
  and exists (
    select 1 from public.memories m
    where m.id = memory_id and m.user_id = auth.uid()
  )
);

create policy if not exists "records insert by owner" on public.memory_records
for insert with check (
  auth.uid() = user_id
  and exists (
    select 1 from public.memories m
    where m.id = memory_id and m.user_id = auth.uid()
  )
);

create policy if not exists "records update by owner" on public.memory_records
for update using (
  auth.uid() = user_id
  and exists (
    select 1 from public.memories m
    where m.id = memory_id and m.user_id = auth.uid()
  )
) with check (
  auth.uid() = user_id
  and exists (
    select 1 from public.memories m
    where m.id = memory_id and m.user_id = auth.uid()
  )
);

create policy if not exists "records delete by owner" on public.memory_records
for delete using (
  auth.uid() = user_id
  and exists (
    select 1 from public.memories m
    where m.id = memory_id and m.user_id = auth.uid()
  )
);

-- No URLs to paste here. Rely on project configuration.
