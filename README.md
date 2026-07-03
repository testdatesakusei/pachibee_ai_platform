# PachiBee AI Platform

## 概要

PachiBee AI Platform はパチンコ・パチスロ業界向けのAI分析プラットフォームです。

Machine Intelligence・Hall Intelligence・Market Intelligence・Event Intelligence を中心に、ホール経営者・一般ユーザー向けに分析・予測・レポートを提供します。

---

## フォルダ構成

01_database

SQL

02_import

データ取込

03_output

レポート出力

04_ai_analysis

AIエンジン

05_launcher

ランチャー（予定）

06_web

Web画面

07_api

API（予定）

08_docs

設計書

output

CSV出力

.cursor

Cursorルール

---

## 実行順

① ベースExcel取込

② Feature Snapshot作成

③ Machine Intelligence実行

④ Web起動

---

## Web

06_web

起動

py [app.py](http://app.py)

ブラウザ

[http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 開発ルール

PとSは完全分離

CSV列名変更禁止

既存機能を壊さない

関数化を優先

コメントを書く

---

## Version

v1.0