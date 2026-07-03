# PachiBee AI Platform v1.0 設計書

## 1. 目的

PachiBee AI Platformは、パチンコ・パチスロの機種データ、稼働データ、市場データ、来店・取材情報を統合し、ユーザー向け・ホール向けにAI分析を提供するための基盤である。

## 2. v1.0のゴール

### データ基盤

- ベースExcel340ファイルを読み込む

- 2019年9月4日以降の週次稼働データを管理

- 1,502機種の機種辞書を管理

- 別名辞書を管理

- Source Masterで更新対象を管理

### AI分析

- 人気指数

- 粗利指数

- 寿命指数

- 売却推奨度

- 導入推奨度

- 稼働予測

- AIコメント

### 将来拡張

- 中古価格自動取得

- 全国設置台数

- 機種仕様自動取得

- 来店・取材評価

- ホール分析

- Web公開

- LINE Bot

---

## 3. 全体構成

```text

pachibee_ai_platform

├── 01_database

│   ├── 01_create_tables.sql

│   ├── 02_create_machine_carte_tables.sql

│   ├── 03_create_machine_dictionary_tables.sql

│   ├── 04_alter_machine_dictionary_add_tracking.sql

│   ├── 05_create_source_master.sql

│   └── 06_seed_source_master.sql

│

├── 02_import

│   ├── import_base_[excel.py](http://excel.py)

│   ├── create_machine_[master.py](http://master.py)

│   ├── prepare_machine_dictionary_[import.py](http://import.py)

│   └── upload_machine_dictionary_to_[supabase.py](http://supabase.py)

│

├── 03_collectors

│   ├── machine_specs

│   ├── used_price

│   ├── installation

│   ├── raiten_events

│   ├── media_events

│   └── sns

│

├── 04_ai_analysis

│   ├── build_machine_master_[v2.py](http://v2.py)

│   ├── forecast_[operation.py](http://operation.py)

│   ├── calculate_popularity_[score.py](http://score.py)

│   ├── calculate_profit_[score.py](http://score.py)

│   ├── calculate_lifecycle_[score.py](http://score.py)

│   └── generate_ai_[comment.py](http://comment.py)

│

├── 05_reports

├── 06_web

├── 07_scheduler

├── 08_docs

├── base_files

├── output

├── logs

└── config