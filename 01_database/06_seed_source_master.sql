insert into source_master
(source_key, source_name, source_type, base_url, target_data, update_frequency, schedule_note, is_active, priority, requires_login, legal_note, memo)
values
('base_excel', 'ベースExcel', 'local_file', null, '週次稼働・売上・粗利', 'weekly', '新しいベースExcelをbase_filesへ追加後に実行', true, 1, false, '自社保有データ', '最重要データ'),

('machine_specs', '機種仕様情報', 'web', null, '導入日・スペック・LT・AT・純増・TY・MY・ボーダー等', 'daily', '毎日深夜に新機種中心で更新', true, 2, false, '公開情報の範囲で取得', '機種カルテ補完用'),

('used_price', '中古価格情報', 'web', null, '中古価格・価格変動・売買判断', 'daily', '毎日朝に更新', true, 3, false, '取得元規約確認が必要', '売却タイミング予測用'),

('installation', '全国設置台数', 'web', null, '全国設置台数・増台・減台・店舗数', 'weekly', '週1回更新', true, 4, false, '取得元規約確認が必要', '市場規模・撤去判断用'),

('release_schedule', '新台導入予定', 'web', null, '導入日・販売台数・競合新台', 'weekly', '週1回、月初は重点更新', true, 5, false, '公開情報の範囲で取得', '競合影響分析用'),

('raiten_events', '来店情報', 'web', 'https://raiten-ex.com/', '来店演者・ホール・日付', 'daily', '毎日更新', true, 6, false, 'サイト規約確認が必要', '来店評価用'),

('media_events', '取材情報', 'web', null, '取材名・ホール・日付・媒体', 'daily', '毎日更新', true, 7, false, 'サイト規約確認が必要', '取材評価用'),

('minrepo_hall_data', 'みんレポ系ホールデータ', 'web', 'https://min-repo.com/', 'ホール別全台データ・差枚・G数・出率', 'daily', '対象ホールのみ更新', true, 8, false, 'サイト規約確認が必要', 'ホール分析・明日狙うなら用'),

('sns_x', 'X話題性', 'api_or_web', 'https://x.com/', '機種名の話題量・好意度・炎上/高評価', 'daily', '毎日夜に更新', false, 9, true, 'API利用・規約確認が必要', 'SNS人気補正用'),

('youtube', 'YouTube露出', 'api', 'https://www.youtube.com/', '機種動画数・再生数・投稿者数', 'weekly', '週1回更新', false, 10, true, 'API利用が望ましい', '話題性・若年層人気用')
on conflict (source_key) do update set
  source_name = excluded.source_name,
  source_type = excluded.source_type,
  base_url = excluded.base_url,
  target_data = excluded.target_data,
  update_frequency = excluded.update_frequency,
  schedule_note = excluded.schedule_note,
  is_active = excluded.is_active,
  priority = excluded.priority,
  requires_login = excluded.requires_login,
  legal_note = excluded.legal_note,
  memo = excluded.memo,
  updated_at = now();