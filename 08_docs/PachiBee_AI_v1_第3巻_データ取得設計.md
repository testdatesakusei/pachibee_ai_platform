# PachiBee AI Platform v1.0

# 第3巻 データ取得設計

Version 1.0

---

# 1. 本書の目的

PachiBee AI Platform が利用する全データの取得方法・更新方法・更新頻度・品質管理方法を定義する。

本書で扱うデータは以下とする。

・ベースデータ

・中古価格

・全国設置台数

・新台情報

・ホール情報

・イベント情報

・来店情報

・SNS

・YouTube

・Google Trends

・その他外部データ

---

# 2. 全体データフロー

```text

                外部サイト

        ┌──────────────┐

        │ベースExcel     │

        │中古価格       │

        │設置台数       │

        │来店情報       │

        │取材情報       │

        │SNS           │

        │YouTube       │

        └──────┬───────┘

               │

         Data Import Engine

               │

        Data Cleaning Engine

               │

      Feature Generation Engine

               │

         Supabase Database

               │

        Intelligence Engine

               │

        ChatGPT / Web / API

```

---



# 3. データ分類

|分類|内容|更新|

|----|----|----|

|内部データ|ベースExcel|毎週|

|市場データ|中古価格・設置台数|毎日|

|店舗データ|ホール情報|毎日|

|イベントデータ|来店・取材|毎日|

|SNSデータ|X・YouTube|毎日|

|予測データ|AI生成|毎日|

---



# 4. ベースExcel



## データ内容

週次実績

取得項目

・稼働

・売上

・粗利

・粗利率

・台数

・導入週

---



## 更新

毎週

更新担当

Launcher

実行

```text

Base Excel

↓

import_base_[excel.py](http://excel.py)

↓

prepare_weekly_performance_[import.py](http://import.py)

↓

Supabase

```

---



# 5. 中古価格

目的

市場価値を取得する。

取得項目

・機種

・価格

・前日比

・前週比

・更新日

・販売店

・在庫数

---

更新

毎日

保存先

market_price_history

---



# 6. 全国設置台数

取得項目

・設置店舗数

・設置台数

・前週比

・増台数

・減台数

更新

毎日

保存

market_installation_history

---



# 7. 新台情報

取得項目

・メーカー

・シリーズ

・販売予定日

・導入開始日

・販売台数

・タイプ

更新

毎月

---



# 8. ホール情報

取得

全国ホール

保存

hall_master

取得項目

・店舗名

・住所

・都道府県

・設置台数

・営業形態

・グランド

・リニューアル

更新

毎週

---



# 9. 来店・取材

取得

媒体

演者

保存

event_master

visitor_master

取得項目

・開催日

・店舗

・媒体

・演者

・公約

・評価

更新

毎日

---



# 10. SNS

対象

X

Instagram

YouTube

Google Trends

取得項目

・投稿数

・動画数

・再生数

・検索指数

・エンゲージメント

更新

毎日

---



# 11. データ品質管理

すべてのデータは取り込み時に検証を行う。

チェック内容

・NULL

・重複

・異常値

・カテゴリ不一致

・P/S混在

・日付異常

・数値異常

エラーは

source_update_log

へ保存する。

---



# 12. 自動更新スケジュール

05:00

市場データ

↓

06:00

SNS

↓

07:00

イベント

↓

08:00

AI再計算

↓

09:00

Supabase更新

↓

10:00

Web更新

---



# 13. 更新優先順位

★★★★★

ベースExcel

★★★★★

中古価格

★★★★★

設置台数

★★★★☆

イベント

★★★★☆

来店

★★★☆☆

SNS

★★★☆☆

YouTube

★★☆☆☆

Google Trends

---



# 14. 更新失敗時

自動リトライ

最大3回

失敗時

メール通知

ログ保存

管理画面表示

---



# 15. 第4巻

次巻では

・Web画面設計

・API設計

・ユーザー画面

・ホール画面

・AIチャット画面

・管理画面

を設計する。