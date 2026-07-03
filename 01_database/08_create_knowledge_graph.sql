-- ==========================================
-- PachiBee Knowledge Graph
-- ==========================================

-----------------------------------
-- IP（作品）
-----------------------------------

create table if not exists ip_master (

    id bigserial primary key,

    ip_name text not null unique,

    ip_type text,

    original_author text,

    publisher text,

    animation_company text,

    first_release_year int,

    memo text,

    created_at timestamp default now(),

    updated_at timestamp default now()

);

-----------------------------------
-- ゲームシステム
-----------------------------------

create table if not exists game_system_master (

    id bigserial primary key,

    system_name text not null unique,

    category text,

    memo text,

    created_at timestamp default now()

);

-----------------------------------
-- スペックマスター
-----------------------------------

create table if not exists spec_master (

    id bigserial primary key,

    machine_id text,

    category text,

    machine_type text,

    is_smart boolean,

    is_lt boolean,

    is_bt boolean,

    at_art text,

    coin_value numeric,

    my numeric,

    ty numeric,

    base_game numeric,

    pure_increase numeric,

    cz_probability numeric,

    at_probability numeric,

    bonus_probability numeric,

    initial_investment numeric,

    average_out numeric,

    ceiling_game numeric,

    expected_payback numeric,

    memo text,

    created_at timestamp default now(),

    updated_at timestamp default now()

);

-----------------------------------
-- 機種特徴
-----------------------------------

create table if not exists feature_master (

    id bigserial primary key,

    feature_name text unique,

    feature_group text,

    memo text,

    created_at timestamp default now()

);

-----------------------------------
-- 機種⇔特徴
-----------------------------------

create table if not exists machine_feature (

    id bigserial primary key,

    machine_id text,

    feature_id bigint references feature_master(id),

    score numeric,

    memo text

);

-----------------------------------
-- 類似機種
-----------------------------------

create table if not exists similar_machine (

    id bigserial primary key,

    machine_id text,

    similar_machine_id text,

    similarity numeric,

    reason text,

    created_at timestamp default now()

);

-----------------------------------
-- 後継機
-----------------------------------

create table if not exists successor_machine (

    id bigserial primary key,

    before_machine text,

    after_machine text,

    relation_type text,

    memo text

);

-----------------------------------
-- AIスコア履歴
-----------------------------------

create table if not exists ai_score_history (

    id bigserial primary key,

    machine_id text,

    report_date date,

    popularity_score numeric,

    profit_score numeric,

    lifecycle_score numeric,

    asset_score numeric,

    overall_score numeric,

    ai_comment text,

    created_at timestamp default now()

);

-----------------------------------
-- 市場データ
-----------------------------------

create table if not exists market_history (

    id bigserial primary key,

    machine_id text,

    report_date date,

    used_price numeric,

    installed_halls int,

    installed_units int,

    market_rank int,

    memo text,

    created_at timestamp default now()

);

-----------------------------------
-- SNS話題量
-----------------------------------

create table if not exists sns_history (

    id bigserial primary key,

    machine_id text,

    report_date date,

    x_count int,

    youtube_count int,

    tiktok_count int,

    total_score numeric,

    created_at timestamp default now()

);

-----------------------------------
-- AIコメント辞書
-----------------------------------

create table if not exists ai_comment_template (

    id bigserial primary key,

    comment_type text,

    score_min numeric,

    score_max numeric,

    template text,

    created_at timestamp default now()

);

-----------------------------------
-- INDEX
-----------------------------------

create index if not exists idx_spec_machine
on spec_master(machine_id);

create index if not exists idx_feature_machine
on machine_feature(machine_id);

create index if not exists idx_similar_machine
on similar_machine(machine_id);

create index if not exists idx_market_machine
on market_history(machine_id);

create index if not exists idx_sns_machine
on sns_history(machine_id);

create index if not exists idx_ai_history_machine
on ai_score_history(machine_id);