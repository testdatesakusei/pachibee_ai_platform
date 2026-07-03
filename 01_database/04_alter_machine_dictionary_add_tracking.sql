-- ==========================================
-- machine_dictionary 拡張
-- 情報取得元・更新管理・型式名などを追加
-- ==========================================

alter table public.machine_dictionary
add column if not exists model_code text;

alter table public.machine_dictionary
add column if not exists certification_number text;

alter table public.machine_dictionary
add column if not exists official_url text;

alter table public.machine_dictionary
add column if not exists source_name text;

alter table public.machine_dictionary
add column if not exists source_url text;

alter table public.machine_dictionary
add column if not exists source_checked_at timestamp;

alter table public.machine_dictionary
add column if not exists spec_updated_at timestamp;

alter table public.machine_dictionary
add column if not exists market_updated_at timestamp;

alter table public.machine_dictionary
add column if not exists last_auto_update_at timestamp;

alter table public.machine_dictionary
add column if not exists update_status text default 'pending';

alter table public.machine_dictionary
add column if not exists data_quality_score numeric;

alter table public.machine_dictionary
add column if not exists data_quality_comment text;

create index if not exists idx_machine_dictionary_model_code
on public.machine_dictionary(model_code);

create index if not exists idx_machine_dictionary_update_status
on public.machine_dictionary(update_status);