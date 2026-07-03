-- PachiBee AI Platform 基本テーブル
-- Supabase SQL Editor に貼り付けて Run

create table if not exists makers (
  id bigserial primary key,
  maker_name text not null unique,
  created_at timestamp default now()
);

create table if not exists machines (
  id bigserial primary key,
  machine_name text not null,
  maker_name text,
  category text,
  machine_type text,
  release_date date,
  spec_ts text,
  is_smart boolean default false,
  is_lt boolean default false,
  is_bt boolean default false,
  coin_unit_price numeric,
  base_game numeric,
  ty numeric,
  my numeric,
  pure_increase numeric,
  ceiling_info text,
  game_feature text,
  roughness_score numeric,
  setting_dependency_score numeric,
  repeat_score numeric,
  lifecycle_type text,
  created_at timestamp default now(),
  updated_at timestamp default now()
);

create table if not exists machine_weekly_performance (
  id bigserial primary key,
  source_file text,
  report_date date,
  category text,
  rank integer,
  machine_name text,
  maker_name text,
  spec_ts text,
  delivery_date text,
  units integer,
  operation numeric,
  sales numeric,
  gross_profit numeric,
  payout_rate numeric,
  unit_price numeric,
  unit_profit numeric,
  elapsed_week numeric,
  created_at timestamp default now()
);

create table if not exists machine_market_price (
  id bigserial primary key,
  machine_name text not null,
  maker_name text,
  market_date date,
  used_price numeric,
  price_rank integer,
  previous_price numeric,
  price_change numeric,
  created_at timestamp default now()
);

create table if not exists machine_installation (
  id bigserial primary key,
  machine_name text not null,
  survey_date date,
  installed_units integer,
  increase_units integer,
  decrease_units integer,
  stores integer,
  created_at timestamp default now()
);

create table if not exists machine_release_schedule (
  id bigserial primary key,
  machine_name text not null,
  maker_name text,
  category text,
  release_date date,
  planned_units integer,
  notes text,
  created_at timestamp default now()
);

create table if not exists machine_operation_forecast (
  id bigserial primary key,
  forecast_date date not null,
  machine_name text not null,
  category text,
  predicted_operation numeric,
  predicted_rank integer,
  confidence_score numeric,
  reason text,
  created_at timestamp default now()
);

create table if not exists machine_ai_evaluation (
  id bigserial primary key,
  evaluation_date date not null,
  machine_name text not null,
  category text,
  operation_grade text,
  profit_grade text,
  lifecycle_grade text,
  buy_recommendation text,
  sell_recommendation text,
  risk_comment text,
  ai_comment text,
  created_at timestamp default now()
);

create table if not exists halls (
  id bigserial primary key,
  hall_name text not null,
  area text,
  prefecture text,
  city text,
  address text,
  p_count integer,
  s_count integer,
  old_event_days text,
  created_at timestamp default now()
);

create table if not exists hall_events (
  id bigserial primary key,
  hall_name text not null,
  event_date date,
  event_name text,
  event_type text,
  organizer text,
  importance_score numeric,
  created_at timestamp default now()
);

create table if not exists influencer_visits (
  id bigserial primary key,
  influencer_name text not null,
  visit_date date,
  hall_name text,
  event_name text,
  operation_change numeric,
  sales_change numeric,
  evaluation_score numeric,
  created_at timestamp default now()
);

create table if not exists import_jobs (
  id bigserial primary key,
  job_name text not null,
  source_name text,
  started_at timestamp default now(),
  finished_at timestamp,
  status text,
  imported_count integer default 0,
  error_message text,
  created_at timestamp default now()
);

create index if not exists idx_weekly_machine_name on machine_weekly_performance(machine_name);
create index if not exists idx_weekly_report_date on machine_weekly_performance(report_date);
create index if not exists idx_weekly_category on machine_weekly_performance(category);
create index if not exists idx_market_machine on machine_market_price(machine_name);
create index if not exists idx_forecast_date on machine_operation_forecast(forecast_date);

create or replace view v_machine_operation_summary as
select
  machine_name,
  category,
  maker_name,
  count(*) as data_count,
  min(report_date) as first_report_date,
  max(report_date) as latest_report_date,
  avg(operation) as avg_operation,
  max(operation) as max_operation,
  min(operation) as min_operation,
  avg(gross_profit) as avg_gross_profit,
  avg(unit_profit) as avg_unit_profit
from machine_weekly_performance
group by machine_name, category, maker_name;
