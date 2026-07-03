-- ==========================================
-- AI Rule Master
-- AI評価ルール・重み管理
-- ==========================================

create table if not exists ai_rule_master (

    id bigserial primary key,

    rule_key text not null unique,
    rule_name text not null,

    target_type text not null,
    ai_version text default 'v2',

    description text,

    is_active boolean default true,

    created_at timestamp default now(),
    updated_at timestamp default now()
);

create table if not exists ai_rule_weight (

    id bigserial primary key,

    rule_key text not null,
    feature_code text not null,

    feature_name text,

    weight numeric not null,

    direction text default 'positive',

    memo text,

    created_at timestamp default now(),
    updated_at timestamp default now(),

    unique(rule_key, feature_code)
);

create table if not exists ai_rule_grade (

    id bigserial primary key,

    rule_key text not null,

    grade text not null,
    score_min numeric not null,
    score_max numeric not null,

    label text,
    memo text,

    created_at timestamp default now(),

    unique(rule_key, grade)
);

create table if not exists ai_rule_comment_template (

    id bigserial primary key,

    rule_key text not null,
    grade text,

    template_title text,
    template_body text,

    created_at timestamp default now()
);

create index if not exists idx_ai_rule_weight_rule
on ai_rule_weight(rule_key);

create index if not exists idx_ai_rule_grade_rule
on ai_rule_grade(rule_key);

create index if not exists idx_ai_comment_template_rule
on ai_rule_comment_template(rule_key);