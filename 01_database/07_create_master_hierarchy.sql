-- ==========================================
-- 6階層マスター構造
-- メーカー → ブランド → シリーズ → 機種 → 型式 → 週次データ
-- ==========================================

create table if not exists maker_master (
  id bigserial primary key,
  maker_name text not null unique,
  maker_group text,
  memo text,
  created_at timestamp default now(),
  updated_at timestamp default now()
);

create table if not exists brand_master (
  id bigserial primary key,
  brand_name text not null,
  maker_id bigint references maker_master(id),
  category_hint text,
  memo text,
  created_at timestamp default now(),
  updated_at timestamp default now(),
  unique(brand_name, maker_id)
);

create table if not exists series_hierarchy_master (
  id bigserial primary key,
  series_name text not null,
  brand_id bigint references brand_master(id),
  parent_series_id bigint references series_hierarchy_master(id),
  category_hint text,
  memo text,
  created_at timestamp default now(),
  updated_at timestamp default now(),
  unique(series_name, brand_id)
);

create table if not exists machine_hierarchy_master (
  id bigserial primary key,
  machine_id text not null unique,
  formal_machine_name text not null,
  category text not null,
  maker_id bigint references maker_master(id),
  brand_id bigint references brand_master(id),
  series_id bigint references series_hierarchy_master(id),
  current_dictionary_id bigint references machine_dictionary(id),
  machine_type text,
  release_date date,
  first_report_date date,
  latest_report_date date,
  is_active boolean default true,
  memo text,
  created_at timestamp default now(),
  updated_at timestamp default now()
);

create table if not exists model_code_master (
  id bigserial primary key,
  machine_hierarchy_id bigint references machine_hierarchy_master(id),
  model_code text,
  certification_number text,
  spec_name text,
  release_date date,
  memo text,
  created_at timestamp default now(),
  updated_at timestamp default now(),
  unique(machine_hierarchy_id, model_code)
);

create table if not exists hierarchy_alias_master (
  id bigserial primary key,
  alias_name text not null,
  alias_type text not null,
  target_table text not null,
  target_id bigint,
  confidence_score numeric,
  memo text,
  created_at timestamp default now()
);

create index if not exists idx_brand_maker_id
on brand_master(maker_id);

create index if not exists idx_series_brand_id
on series_hierarchy_master(brand_id);

create index if not exists idx_machine_hierarchy_machine_id
on machine_hierarchy_master(machine_id);

create index if not exists idx_machine_hierarchy_category
on machine_hierarchy_master(category);

create index if not exists idx_machine_hierarchy_series_id
on machine_hierarchy_master(series_id);

create index if not exists idx_model_code_machine_id
on model_code_master(machine_hierarchy_id);

create index if not exists idx_hierarchy_alias_name
on hierarchy_alias_master(alias_name);