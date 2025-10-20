-- 30_chat_messages.sql
-- Requires: 10_memories.sql

create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  memory_id uuid not null references public.memories(id) on delete cascade,
  role text not null check (role in ('user','assistant','system')),
  content text not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_chat_memory on public.chat_messages(memory_id);
create index if not exists idx_chat_user on public.chat_messages(user_id);
create index if not exists idx_chat_user_memory_created on public.chat_messages(user_id, memory_id, created_at desc);

alter table public.chat_messages enable row level security;

create policy if not exists "chat select by owner" on public.chat_messages
for select using (
  auth.uid() = user_id
  and exists (
    select 1 from public.memories m
    where m.id = memory_id and m.user_id = auth.uid()
  )
);

create policy if not exists "chat insert by owner" on public.chat_messages
for insert with check (
  auth.uid() = user_id
  and exists (
    select 1 from public.memories m
    where m.id = memory_id and m.user_id = auth.uid()
  )
);

create policy if not exists "chat update by owner" on public.chat_messages
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

create policy if not exists "chat delete by owner" on public.chat_messages
for delete using (
  auth.uid() = user_id
  and exists (
    select 1 from public.memories m
    where m.id = memory_id and m.user_id = auth.uid()
  )
);

-- Rolling-window retention: keep last 10 messages per (user_id, memory_id).
-- This runs AFTER each insert and deletes any older rows beyond the top 10.
create or replace function public.prune_chat_messages()
returns trigger as $$
begin
  delete from public.chat_messages c
  using (
    select id
    from public.chat_messages
    where user_id = NEW.user_id
      and memory_id = NEW.memory_id
    order by created_at desc, id desc
    offset 10
  ) old
  where c.id = old.id;
  return null; -- AFTER trigger ignores returned row
end;
$$ language plpgsql;

drop trigger if exists trg_prune_chat_messages on public.chat_messages;
create trigger trg_prune_chat_messages
  after insert on public.chat_messages
  for each row
  execute function public.prune_chat_messages();

-- No URLs to paste here. Keys/URLs are used by applications, not schema.
