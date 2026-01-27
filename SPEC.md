# Project Specification: Japan Macro Dashboard (J-Macro)

## 1. プロジェクトの目的 (Objectives)
日本の政府統計（e-Stat API）を活用し、マクロ経済の「三面等価（生産・分配・支出）」を可視化するダッシュボードを構築する。
ユーザーはデータアナリストであり、主な目的は以下の2点である。

1.  **投資判断:**
    * 景気の先行指標・遅行指標を組み合わせ、構造的なトレンド（インフレ、人手不足、在庫循環）を把握し、有望なセクターを選定するための仮説生成を行う。
2.  **家計防衛:**
    * 賃金上昇と物価上昇の乖離（実質賃金）や、消費支出のトレンドを把握し、自身の家計管理に活かす。

## 2. 分析アプローチ (Analysis Scope)
以下の「経済の三連星」に基づき、段階的にデータを実装する。

### Phase 1: 分配 (Distribution) - 最優先
* **対象統計:** 毎月勤労統計調査 (Monthly Labour Survey)
* **KPI:** 現金給与総額、実質賃金指数、総実労働時間、常用雇用指数
* **問い:** 「名目賃金は上がっているが、インフレに勝てているか？」「パートタイム（タイミー領域）の賃金動向は？」

### Phase 2: 生産 (Production)
* **対象統計:** 鉱工業指数 (Indices of Industrial Production) / 第3次産業活動指数
* **KPI:** 生産指数、出荷指数、在庫指数
* **問い:** 「在庫循環図における現在の位置はどこか？（意図せぬ在庫増の兆候はあるか）」

### Phase 3: 支出 (Expenditure)
* **対象統計:** 家計調査 (Family Income and Expenditure Survey)
* **KPI:** 品目別支出金額、購入頻度
* **問い:** 「インフレ下で消費者が財布の紐を締めている品目は何か？」

## 3. アーキテクチャ (Technical Architecture)
Google Cloud を用いたサーバーレスELT構成とする。

* **Extract (収集):**
    * **Runtime:** Cloud Run Jobs (Python 3.11+)
    * **Logic:** e-Stat APIからJSONを取得し、DataFrame化してBigQueryへロード。
    * **Infrastructure:** Terraform管理。Dockerコンテナ化。
* **Load (蓄積):**
    * **DWH:** BigQuery (Region: asia-northeast1)
    * **Dataset:** `raw_layer` (生データ保管)
* **Transform (加工):**
    * **Tool:** dbt Core (SQL-based transformation)
    * **Dataset:** `dwh_layer` (クレンジング済), `mart_layer` (可視化用集計)
* **Visualize (可視化):**
    * **Tool:** Looker Studio (Connects to BigQuery `mart_layer`)

## 4. ディレクトリ構成 (Proposed Structure)
```text
.
├── infra/                  # Terraform (Cloud Run, BigQuery, Scheduler)
├── src/                    # Application Code
│   ├── extract/            # Python Scripts for API Extraction
│   │   ├── main.py         # Entry point
│   │   ├── client.py       # e-Stat API Client class
│   │   └── Dockerfile
│   └── transform/          # dbt Project
│       ├── models/
│       └── dbt_project.yml
└── SPEC.md                 # This Specification file