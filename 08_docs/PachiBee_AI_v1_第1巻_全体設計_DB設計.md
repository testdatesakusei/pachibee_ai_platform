# PachiBee AI Platform v1.0  

# 第1巻：全体設計・システム構成・DB設計

## 1. プロジェクト概要

PachiBee AI Platformは、パチンコ・パチスロ業界向けのAIデータ分析基盤である。

主な目的は、以下の情報を統合し、ユーザー向け・ホール向けに実用的なAI判断を提供することである。

- ベースExcel稼働データ

- 機種仕様

- 中古価格

- 全国設置台数

- 新台情報

- ホール実績

- 来店情報

- 取材情報

- SNS・YouTube話題性

---

## 2. 現在の到達点

### 2.1 取込済みデータ

- ベースExcel：約340ファイル

- データ開始日：2019年9月4日

- 週次実績：約34,000件

- 機種数：1,499機種

- P/S分類：Sheet1=パチンコ、Sheet2=パチスロで固定済み

- P/S混在問題：解消済み

---

## 3. システム全体構成

```text

PachiBee AI Platform

├── Data Layer

│   ├── ベースExcel

│   ├── 中古価格

│   ├── 全国設置台数

│   ├── 新台情報

│   ├── 来店・取材

│   └── SNS・YouTube

│

├── Database Layer

│   ├── Supabase

│   ├── Machine Master

│   ├── Feature Store

│   ├── Knowledge Graph

│   └── AI Score

│

├── Intelligence Layer

│   ├── Machine AI

│   ├── Market AI

│   ├── Hall AI

│   ├── Event AI

│   └── Prediction AI

│

├── Application Layer

│   ├── Launcher

│   ├── Web

│   ├── LINE Bot

│   └── ChatGPT連携