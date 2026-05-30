create table if not exists assistants (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  business_name text,
  system_prompt text not null,
  language text default 'it',
  voice text default 'alloy',
  email_to text,
  created_at timestamptz default now()
);

create table if not exists faqs (
  id uuid primary key default gen_random_uuid(),
  assistant_id uuid references assistants(id) on delete cascade,
  question text not null,
  answer text not null,
  created_at timestamptz default now()
);

create table if not exists calls (
  id uuid primary key default gen_random_uuid(),
  assistant_id uuid references assistants(id) on delete set null,
  from_number text,
  to_number text,
  transcript text,
  summary text,
  status text default 'completed',
  created_at timestamptz default now()
);
