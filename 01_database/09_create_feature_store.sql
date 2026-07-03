-- ==========================================
-- PachiBee AI Feature Store
-- ==========================================

----------------------------------------
-- Feature Definition
----------------------------------------

create table if not exists feature_definition (

    id bigserial primary key,

    feature_code text not null unique,
    feature_name text not null,

    category text,

    description text,

    data_type text,

    unit text,

    is_active boolean default true,

    created_at timestamp default now(),
    updated_at timestamp default now()

);

----------------------------------------
-- Machine Weekly Feature
----------------------------------------

create table if not exists machine_weekly_feature (

    id bigserial primary key,

    machine_id text not null,

    report_date date not null,

    feature_code text not null,

    feature_value numeric,

    feature_text text,

    feature_rank numeric,

    created_at timestamp default now()

);

----------------------------------------
-- Hall Weekly Feature
----------------------------------------

create table if not exists hall_weekly_feature (

    id bigserial primary key,

    hall_id text,

    report_date date,

    feature_code text,

    feature_value numeric,

    feature_text text,

    created_at timestamp default now()

);

----------------------------------------
-- Machine Trend
----------------------------------------

create table if not exists machine_trend (

    id bigserial primary key,

    machine_id text,

    report_date date,

    operation_trend numeric,

    profit_trend numeric,

    price_trend numeric,

    sns_trend numeric,

    installed_trend numeric,

    created_at timestamp default now()

);

----------------------------------------
-- AI Score
----------------------------------------

create table if not exists machine_ai_score (

    id bigserial primary key,

    machine_id text,

    report_date date,

    popularity_score numeric,

    profit_score numeric,

    lifecycle_score numeric,

    asset_score numeric,

    market_score numeric,

    recommendation_score numeric,

    overall_score numeric,

    ai_comment text,

    created_at timestamp default now()

);

----------------------------------------
-- Ranking History
----------------------------------------

create table if not exists machine_ranking_history (

    id bigserial primary key,

    report_date date,

    category text,

    ranking_type text,

    machine_id text,

    ranking int,

    previous_ranking int,

    ranking_change int,

    score numeric,

    reason text,

    created_at timestamp default now()

);

----------------------------------------
-- Prediction
----------------------------------------

create table if not exists machine_prediction (

    id bigserial primary key,

    machine_id text,

    report_date date,

    target_week date,

    predicted_operation numeric,

    predicted_profit numeric,

    predicted_used_price numeric,

    predicted_installed_units numeric,

    confidence numeric,

    created_at timestamp default now()

);

----------------------------------------
-- Index
----------------------------------------

create index if not exists idx_machine_feature_machine
on machine_weekly_feature(machine_id);

create index if not exists idx_machine_feature_date
on machine_weekly_feature(report_date);

create index if not exists idx_machine_feature_code
on machine_weekly_feature(feature_code);

create index if not exists idx_machine_ai_score
on machine_ai_score(machine_id);

create index if not exists idx_machine_ranking
on machine_ranking_history(machine_id);

create index if not exists idx_machine_prediction
on machine_prediction(machine_id);