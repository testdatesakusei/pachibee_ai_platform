-- ==========================================
-- Source Master
-- 自動収集するデータ元を管理する
-- ==========================================

create table if not exists source_master (
  id bigserial primary key,
  source_key text not null unique,
  source_name text not null,
  source_type text not null,
  base_url text,
  target_data text,
  update_frequency text,
  schedule_note text,
  is_active boolean default true,
  priority integer default 100,
  requires_login boolean default false,
  legal_note text,
  memo text,
  created_at timestamp default now(),
  updated_at timestamp default now()
);

create table if not exists source_update_log (
  id bigserial primary key,
  source_key text not null,
  job_name text,
  started_at timestamp default now(),
  finished_at timestamp,
  status text,
  fetched_count integer default 0,
  inserted_count integer default 0,
  updated_count integer default 0,
  skipped_count integer default 0,
  error_message text,
  log_detail text,
  created_at timestamp default now()
);

create table if not exists source_fetch_queue (
  id bigserial primary key,
  source_key text not null,
  target_key text,
  target_name text,
  fetch_status text default 'pending',
  retry_count integer default 0,
  scheduled_at timestamp default now(),
  fetched_at timestamp,
  error_message text,
  created_at timestamp default now()
);

create index if not exists idx_source_master_key
on source_master(source_key);

create index if not exists idx_source_update_log_key
on source_update_log(source_key);

create index if not exists idx_source_fetch_queue_status
on source_fetch_queue(fetch_status);