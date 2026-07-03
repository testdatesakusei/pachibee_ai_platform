# AI Intelligence Platform

## 完成設計書 v1.0

---

# 1. プロジェクト概要

## 1.1 目的

AIを活用し、パチンコ・パチスロホールの経営判断を支援するプラットフォームを構築する。

本システムは、

- 市場分析

- 機種分析

- ホール分析

- 来店・取材分析

- AIによる経営アドバイス

を一つのシステムで提供することを目的とする。

---

# 1.2 コンセプト

**「ホール経営者が毎朝最初に開くAIダッシュボード」**

単なるデータ閲覧ツールではなく、

AIが

- 今日何をするべきか

- 今週何を導入するべきか

- 何を売却するべきか

まで提案する。

---

# 1.3 開発方針

本システムは以下の方針で開発する。

- Python

- Flask

- Pandas

- HTML

- CSS

- JavaScript

- SQLite（開発）

- PostgreSQL（本番）

- Chart.js

- OpenAI API

---

# 2. システム全体構成

```

AI Intelligence Platform

│

├ Dashboard

│

├ Machine Intelligence

│

├ Hall Intelligence

│

├ Market Intelligence

│

├ Event Intelligence

│

├ Forecast

│

├ Reports

│

├ AI Advisor

│

└ Settings

```

---

# 3. Dashboard

## 役割

毎日の状況を3分で把握する画面。

### 表示内容

・Today's Brief

・AI Summary

・導入推奨

・撤去候補

・市場概況

・最新更新情報

・AIおすすめ機種

・検索

・ランキング

Dashboardは入口であり、

詳細分析は各モジュールで行う。

---

# 4. Machine Intelligence

## 役割

機種単位の分析を行う。

### 機能

・検索

・オートコンプリート

・比較

・AIスコア

・人気分析

・利益分析

・寿命分析

・資産価値分析

・中古価格

・設置店舗

・推移グラフ

・AIコメント

・AI判定

・関連機種

---

# 5. Hall Intelligence

## 役割

店舗単位の分析を行う。

### 表示内容

・店舗基本情報

・営業評価

・AIスコア

・旧イベント評価

・曜日分析

・機種構成分析

・利益分析

・稼働分析

・ジャグラー分析

・スマスロ分析

・増台候補

・撤去候補

・AI改善提案

---

# 6. データベース設計

## 6.1 基本方針

本システムは「分析基盤」として設計する。

CSVをそのまま読むのではなく、

最終的にはデータベースへ格納し、

AI分析・検索・レポート生成を高速化する。

開発時

SQLite

本番

PostgreSQL

を採用する。

---

# 6.2 データ構成

AI Platform

│

├ Machine Master

├ Weekly Performance

├ Market Data

├ Store Master

├ Hall Performance

├ Event Master

├ Entertainer Master

├ Used Price

├ AI Score

└ AI Log

---

# 6.3 Machine Master

全機種のマスターデータ

主キー

machine_id

項目

・機種名

・メーカー

・カテゴリ

・タイプ

・導入日

・導入価格

・販売台数

・AT

・ART

・ノーマル

・スマスロ

・6.5号機

・P機

・e機

・撤去予定

---

# 6.4 Weekly Performance

毎週取り込むデータ

主キー

week

machine_id

項目

・アウト

・売上

・粗利

・粗利率

・稼働

・勝率

・平均MY

・平均差枚

・設置店舗数

・ランキング

---

# 6.5 Market Data

市場情報

項目

・中古価格

・価格推移

・設置店舗数

・増台店舗数

・減台店舗数

・検索数

・SNS件数

・メーカー情報

・市場評価

---

# 6.6 Hall Master

ホール情報

項目

・店舗名

・法人

・住所

・総台数

・P台数

・S台数

・旧イベント

・営業タイプ

・営業地域

---

# 6.7 Hall Performance

店舗実績

項目

・日付

・店舗

・機種

・アウト

・売上

・粗利

・平均設定推定

・稼働率

・勝率

・平均差枚

---

# 6.8 Event Master

取材

来店

イベント

項目

・イベント名

・演者

・媒体

・評価

・平均差枚

・平均出率

・信頼度

・価格

・地域別評価

---

# 6.9 AI Score

AIが計算する結果

項目

・人気指数

・利益指数

・寿命指数

・市場指数

・資産指数

・総合指数

・BUY

・KEEP

・WATCH

・SELL

・AIコメント

・判断根拠

---

# 6.10 AI Log

AIの判断履歴

項目

・日時

・AIモデル

・入力

・出力

・信頼度

・処理時間

・バージョン

---

# 7 データ更新フロー

CSV取込

↓

データチェック

↓

Machine Master更新

↓

Weekly Performance更新

↓

Market更新

↓

AI再計算

↓

Web更新

↓

PDF更新

---

# 8 更新頻度

Machine Master

必要時

Weekly

毎週

中古価格

毎日

市場データ

毎日

イベント

毎日

AI Score

毎日

Web

リアルタイム

