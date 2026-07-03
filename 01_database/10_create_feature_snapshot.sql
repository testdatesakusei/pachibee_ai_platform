-- ==========================================
-- PachiBee AI Feature Snapshot
-- AI・Web表示用 高速参照テーブル
-- ==========================================

create table if not exists machine_feature_snapshot (

    id bigserial primary key,

    machine_id text not null,
    machine_name text,
    category text,
    report_date date not null,

    ------------------------------------------------
    -- 基本情報
    ------------------------------------------------

    maker_name text,
    brand_name text,
    series_name text,

    machine_type text,

    is_smart boolean,
    is_lt boolean,
    is_bt boolean,

    ------------------------------------------------
    -- 稼働
    ------------------------------------------------

    latest_operation numeric,
    avg_operation_4w numeric,
    avg_operation_12w numeric,
    avg_operation_all numeric,

    max_operation numeric,
    min_operation numeric,

    operation_trend_4w numeric,
    operation_trend_12w numeric,

    operation_contribution_weeks numeric,

    ------------------------------------------------
    -- 売上
    ------------------------------------------------

    latest_sales numeric,
    avg_sales_4w numeric,
    avg_sales_12w numeric,
    avg_sales_all numeric,

    ------------------------------------------------
    -- 粗利
    ------------------------------------------------

    latest_gross_profit numeric,
    avg_gross_profit_4w numeric,
    avg_gross_profit_12w numeric,
    avg_gross_profit_all numeric,

    profit_tolerance_score numeric,

    ------------------------------------------------
    -- 市場
    ------------------------------------------------

    used_price numeric,
    used_price_change_rate numeric,

    installed_halls integer,
    installed_units integer,

    installed_units_change_rate numeric,

    ------------------------------------------------
    -- SNS
    ------------------------------------------------

    x_score numeric,
    youtube_score numeric,
    tiktok_score numeric,

    sns_score numeric,

    ------------------------------------------------
    -- AI
    ------------------------------------------------

    popularity_score numeric,
    profit_score numeric,
    lifecycle_score numeric,
    market_score numeric,
    asset_score numeric,
    recommendation_score numeric,

    overall_score numeric,
    overall_grade text,

    ------------------------------------------------
    -- コメント
    ------------------------------------------------

    score_reason text,

    ai_comment text,

    ------------------------------------------------

    created_at timestamp default now(),
    updated_at timestamp default now(),

    unique(machine_id, report_date)

);

------------------------------------------------
-- Index
------------------------------------------------

create index if not exists idx_snapshot_machine
on machine_feature_snapshot(machine_id);

create index if not exists idx_snapshot_date
on machine_feature_snapshot(report_date);

create index if not exists idx_snapshot_category
on machine_feature_snapshot(category);

create index if not exists idx_snapshot_score
on machine_feature_snapshot(overall_score);

create index if not exists idx_snapshot_popularity
on machine_feature_snapshot(popularity_score);