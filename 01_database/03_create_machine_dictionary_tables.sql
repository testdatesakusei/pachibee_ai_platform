-- ==========================================
-- STEP：機種辞書DB
-- 北斗・海・ジャグラーなどを雑に統合しないための辞書
-- ==========================================

create table if not exists series_master (
  id bigserial primary key,
  series_name text not null unique,
  category_hint text,
  memo text,
  created_at timestamp default now()
);

create table if not exists machine_dictionary (
  id bigserial primary key,
  machine_id text not null unique,
  formal_machine_name text not null,
  category text not null,
  maker_name text,
  series_name text,
  sub_series_name text,
  spec_name text,
  machine_type text,
  is_smart boolean default false,
  is_lt boolean default false,
  is_bt boolean default false,
  release_date date,
  first_report_date date,
  latest_report_date date,
  data_count integer,
  avg_operation numeric,
  avg_sales numeric,
  avg_gross_profit numeric,
  classification_status text default 'auto',
  review_required boolean default false,
  memo text,
  created_at timestamp default now(),
  updated_at timestamp default now()
);

create table if not exists machine_alias (
  id bigserial primary key,
  alias_name text not null,
  machine_id text not null,
  formal_machine_name text not null,
  confidence_score numeric,
  memo text,
  created_at timestamp default now()
);

create table if not exists machine_classification_review (
  id bigserial primary key,
  raw_machine_name text not null,
  suggested_machine_id text,
  suggested_formal_machine_name text,
  suggested_category text,
  suggested_series_name text,
  suggested_sub_series_name text,
  suggested_machine_type text,
  reason text,
  review_status text default 'pending',
  reviewed_machine_id text,
  reviewed_formal_machine_name text,
  reviewed_by text,
  reviewed_at timestamp,
  created_at timestamp default now()
);

create index if not exists idx_series_master_name
on series_master(series_name);

create index if not exists idx_machine_dictionary_name
on machine_dictionary(formal_machine_name);

create index if not exists idx_machine_dictionary_category
on machine_dictionary(category);

create index if not exists idx_machine_dictionary_series
on machine_dictionary(series_name);

create index if not exists idx_machine_alias_alias
on machine_alias(alias_name);

create index if not exists idx_machine_alias_machine_id
on machine_alias(machine_id);

create index if not exists idx_machine_review_status
on machine_classification_review(review_status);