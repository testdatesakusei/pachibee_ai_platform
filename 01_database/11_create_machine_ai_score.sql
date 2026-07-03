-- ==========================================
-- Machine AI Score
-- AIスコア結果専用テーブル
-- ==========================================

create table if not exists machine_ai_score_result (

    id bigserial primary key,

    machine_id text,
    machine_name text,
    category text,

    report_date date not null,

    ai_version text default 'v2',

    -- ランキング
    overall_rank integer,
    active_rank integer,
    profit_rank integer,
    lifecycle_rank integer,

    -- AIスコア
    active_popularity_score numeric,
    profit_score numeric,
    lifecycle_score numeric,
    asset_score numeric,
    market_score numeric,
    sns_score numeric,
    overall_score numeric,
    overall_grade text,

    -- 元になる補助スコア
    current_operation_score numeric,
    latest_operation_score numeric,
    trend_score numeric,
    profit_power_score numeric,
    profit_stability_score numeric,
    lifecycle_power_score numeric,
    market_power_score numeric,
    sns_power_score numeric,

    -- 説明
    score_reason text,
    ai_comment text,

    created_at timestamp default now(),
    updated_at timestamp default now(),

    unique(machine_id, report_date, ai_version)
);

create table if not exists machine_ai_reason (

    id bigserial primary key,

    machine_id text,
    machine_name text,
    category text,

    report_date date not null,
    ai_version text default 'v2',

    reason_type text,
    reason_title text,
    reason_detail text,
    impact_score numeric,

    created_at timestamp default now()
);

create index if not exists idx_ai_score_result_machine
on machine_ai_score_result(machine_id);

create index if not exists idx_ai_score_result_date
on machine_ai_score_result(report_date);

create index if not exists idx_ai_score_result_category
on machine_ai_score_result(category);

create index if not exists idx_ai_score_result_overall
on machine_ai_score_result(overall_score);

create index if not exists idx_ai_reason_machine
on machine_ai_reason(machine_id);