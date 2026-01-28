# Project Specification: Japan Macro Dashboard (J-Macro)

## 1. プロジェクトの目的 (Objectives)
日本の政府統計（e-Stat）を活用し、マクロ経済の「三面等価（生産・分配・支出）」を可視化するダッシュボードを構築する。
ユーザーはデータアナリストであり、主な目的は以下の2点である。

1.  **投資判断:**
    * 景気の先行指標・遅行指標を組み合わせ、構造的なトレンド（インフレ、人手不足、在庫循環）を把握し、有望なセクターを選定するための仮説生成を行う。
2.  **家計防衛:**
    * 賃金上昇と物価上昇の乖離（実質賃金）や、消費支出のトレンドを把握し、自身の家計管理に活かす。

---

## 2. 分析アプローチ (Analysis Scope)
以下の「経済の三連星」に基づき、段階的にデータを実装する。

### Phase 1: 分配 (Distribution) - ✅ 完了
* **対象統計:** 毎月勤労統計調査 (Monthly Labour Survey)
* **実装状況:**
  * ✅ **指数データ（1952-2025）**: 現金給与総額指数、常用雇用指数、総実労働時間指数
  * ✅ **実数データ（2024-2025）**: 産業別・性別・就業形態別の月次給与データ（円単位）
  * ✅ **自動更新**: GitHub Actionsで毎月25日に最新データを自動取得
  * ✅ **データ品質**: SQLで扱いやすい英文字カラム名、マスターテーブル完備
* **KPI:**
  * 現金給与総額（円）、きまって支給する給与、特別給与（賞与等）
  * 常用労働者数、パートタイム労働者数
  * 総実労働時間、所定外労働時間（残業）
  * 長期トレンド指数（1952年～、2020年=100）
* **分析可能な問い:**
  * 「名目賃金は上がっているが、インフレに勝てているか？」
  * 「パートタイム（タイミー領域）の賃金動向は？」
  * 「産業別の給与格差はどうなっているか？」
  * 「男女間賃金格差の推移は？」
  * 「残業時間（所定外労働）のトレンドは？」

**データファイル:**
- `data/cleaned/actual_wages_historical.csv` (99,765行) - 2024-01～2025-11の詳細データ
- `data/cleaned/wage_index.csv` (147行) - 1952～2025の長期トレンド
- `data/master/industry_master.csv` - 産業分類マスター
- `data/master/gender_master.csv` - 性別マスター
- `data/master/employment_type_master.csv` - 就業形態マスター

### Phase 2: 生産 (Production) - 🔲 未実装
* **対象統計:** 鉱工業指数 (Indices of Industrial Production) / 第3次産業活動指数
* **KPI:** 生産指数、出荷指数、在庫指数
* **問い:** 「在庫循環図における現在の位置はどこか？（意図せぬ在庫増の兆候はあるか）」

### Phase 3: 支出 (Expenditure) - 🔲 未実装
* **対象統計:** 家計調査 (Family Income and Expenditure Survey)
* **KPI:** 品目別支出金額、購入頻度
* **問い:** 「インフレ下で消費者が財布の紐を締めている品目は何か？」

---

## 3. アーキテクチャ (Technical Architecture)
段階的にクラウド化を進める方針。**Phase 1はローカル完結型**として実装済み。

### Phase 1 アーキテクチャ（現在）

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Repository                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  .github/workflows/update-data.yml                           │
│  └─ 毎月25日午前9時（JST）に自動実行                          │
│                                                              │
│  src/extract/                                                │
│  ├─ download_latest_indices.py        # 指数データ取得       │
│  ├─ download_latest_actual_data.py    # 実数データ取得       │
│  ├─ download_historical_actual_data.py # 過去データ取得      │
│  ├─ create_master_tables.py           # マスターテーブル作成 │
│  └─ convert_to_english_columns.py     # カラム名英文字化     │
│                                                              │
│  data/cleaned/  ← SQLで扱いやすいクリーンデータ              │
│  data/master/   ← 産業・性別・就業形態のマスターテーブル      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              e-Stat (政府統計の総合窓口)                      │
│  https://www.e-stat.go.jp/                                   │
│                                                              │
│  - 毎月勤労統計調査の最新データ                               │
│  - 直接ダウンロードURL（認証不要）                            │
│    statInfId + fileKind=4 でExcel取得                        │
└─────────────────────────────────────────────────────────────┘
```

**特徴:**
- ✅ **完全自動化**: GitHub Actionsで月次自動更新
- ✅ **認証不要**: e-Stat公開データの直接ダウンロード
- ✅ **SQL対応**: 英文字カラム名、マスターテーブル完備
- ✅ **バージョン管理**: コード・マスターテーブル・ドキュメントをGit管理
- ⚠️ **データファイル**: 大容量CSVはGitignoreで除外（手動でBigQueryへロード）

### Phase 2 アーキテクチャ（予定）
Google Cloudを用いたサーバーレスELT構成へ移行。

```
Extract (収集)
  └─ Cloud Run Jobs (Python 3.11+)
      ↓
Load (蓄積)
  └─ BigQuery
      ├─ raw_layer (生データ)
      └─ dwh_layer (クレンジング済)
          ↓
Transform (加工)
  └─ dbt Core
      └─ mart_layer (可視化用集計)
          ↓
Visualize (可視化)
  └─ Looker Studio
```

**予定する移行ステップ:**
1. ✅ **ローカル実装** - 完了（Phase 1）
2. 🔄 **BigQueryロード** - 次のステップ
3. 🔲 **dbt変換** - データ集計・加工
4. 🔲 **Looker Studio** - ダッシュボード作成
5. 🔲 **Cloud Run化** - コンテナ化・自動実行

---

## 4. データ構成 (Data Structure)

### 4.1 ディレクトリ構成（現在）
```text
japan-macro-dashboard/
├── .github/
│   └── workflows/
│       └── update-data.yml           # 月次自動更新ワークフロー
│
├── src/
│   ├── extract/                      # データ取得・処理スクリプト
│   │   ├── client.py                 # e-Stat APIクライアント
│   │   ├── download_latest_indices.py        # 指数データ取得
│   │   ├── download_latest_actual_data.py    # 実数データ取得（最新月）
│   │   ├── download_historical_actual_data.py # 過去データ一括取得
│   │   ├── create_master_tables.py           # マスターテーブル作成
│   │   ├── convert_to_english_columns.py     # カラム名英文字化
│   │   └── README.md                         # スクリプト説明書
│   │
│   └── transform/                    # dbt Project (未実装)
│       ├── models/
│       └── dbt_project.yml
│
├── data/
│   ├── cleaned/                      # 分析用クリーンデータ（英文字カラム名）
│   │   ├── actual_wages_historical.csv   # 実数データ（99,765行）
│   │   ├── actual_wages_latest.csv       # 実数データ最新月（4,355行）
│   │   ├── wage_index.csv                # 給与指数（147行）
│   │   ├── employment_index.csv          # 雇用指数（147行）
│   │   ├── hours_index.csv               # 労働時間指数（147行）
│   │   └── README.md                     # データ仕様・SQL例
│   │
│   ├── master/                       # マスターテーブル
│   │   ├── industry_master.csv           # 産業分類（8産業）
│   │   ├── gender_master.csv             # 性別（3区分）
│   │   ├── employment_type_master.csv    # 就業形態（3区分）
│   │   ├── column_dictionary.csv         # カラム定義（31項目）
│   │   └── README.md                     # マスターテーブル仕様
│   │
│   └── DATA_STRUCTURE.md             # データ構造ガイド
│
├── infra/                            # Terraform (未実装)
│   ├── bigquery.tf
│   └── cloud_run.tf
│
├── .gitignore                        # データファイル（CSV）を除外
├── .env.example                      # API Key設定例
├── requirements.txt                  # Python依存パッケージ
└── SPEC.md                           # このファイル
```

### 4.2 データスキーマ

#### 実数データ (actual_wages_historical)
| カラム名（英語） | カラム名（日本語） | データ型 | 説明 |
|-----------------|------------------|---------|------|
| year_month | 年月 | VARCHAR(7) | 調査年月（YYYY-MM） |
| industry_code | 産業コード | VARCHAR(10) | T=全産業、0-9=産業分類 |
| gender | 性別 | VARCHAR(1) | T=全体、M=男性、F=女性 |
| employment_type | 就業形態 | VARCHAR(1) | T=全体、N=一般、P=パート |
| total_cash_earnings | 現金給与総額 | INTEGER | 円 |
| scheduled_cash_earnings | きまって支給する給与 | INTEGER | 円 |
| contractual_cash_earnings | 所定内給与 | INTEGER | 円 |
| overtime_pay | 超過労働給与 | INTEGER | 円 |
| special_cash_earnings | 特別給与 | INTEGER | 円（賞与等） |
| total_working_hours | 総実労働時間 | DECIMAL(5,1) | 時間 |
| overtime_hours | 所定外労働時間 | DECIMAL(5,1) | 時間 |
| regular_workers_current | 常用労働者数 | INTEGER | 人 |

#### 指数データ (wage_index / employment_index / hours_index)
| カラム名 | データ型 | 説明 |
|---------|---------|------|
| year | INTEGER | 年 |
| jan～dec | DECIMAL(6,2) | 各月の指数（2020年=100） |

#### マスターテーブル
- **industry_master**: 産業コード（T, 0, 1, 3, 4, 5, 7, 9）と名称
- **gender_master**: 性別コード（T, M, F）と名称
- **employment_type_master**: 就業形態コード（T, N, P）と名称

---

## 5. 実装済み機能 (Implemented Features)

### 5.1 データ取得
- ✅ e-Statから指数データを直接ダウンロード（1952-2025年、74年分）
- ✅ e-Statから実数データを直接ダウンロード（2024-01～2025-11、23ヶ月分）
- ✅ 月次自動更新（GitHub Actions）
- ✅ statInfId自動取得（指数データ）
- ⚠️ statInfId手動更新（実数データ - 月次で変わるため）

### 5.2 データ処理
- ✅ Excelファイルの自動読み込み（xlrdエンジン）
- ✅ カラム名の英文字化（日本語→英語）
- ✅ データクレンジング（NULL処理、データ型変換）
- ✅ マスターテーブル生成（産業、性別、就業形態、カラム定義）
- ✅ 統合CSV出力（過去23ヶ月を1ファイルに結合）

### 5.3 データ品質
- ✅ SQLで扱いやすい英文字カラム名
- ✅ 主キー設計（year_month + industry_code + gender + employment_type）
- ✅ マスターテーブルによるJOIN対応
- ✅ データディクショナリ（31カラムの詳細定義）
- ✅ バリデーション（数値型変換、欠損値処理）

### 5.4 ドキュメント
- ✅ データ構造ガイド（`data/DATA_STRUCTURE.md`）
- ✅ マスターテーブル仕様（`data/master/README.md`）
- ✅ クリーンデータ仕様（`data/cleaned/README.md`）
- ✅ SQLクエリ例（産業別給与、男女格差、長期トレンド等）
- ✅ BigQueryロード手順

---

## 6. 次のステップ (Next Steps)

### 6.1 即座に実行可能
1. **BigQueryへのデータロード**
   ```bash
   # マスターテーブルのロード
   bq load --source_format=CSV --skip_leading_rows=1 --autodetect \
     japan_macro_dashboard.industry_master data/master/industry_master.csv

   # 実数データのロード
   bq load --source_format=CSV --skip_leading_rows=1 --autodetect \
     japan_macro_dashboard.actual_wages_historical data/cleaned/actual_wages_historical.csv

   # 指数データのロード
   bq load --source_format=CSV --skip_leading_rows=1 --autodetect \
     japan_macro_dashboard.wage_index data/cleaned/wage_index.csv
   ```

2. **dbt変換の実装**
   - `src/transform/models/` に以下のモデルを作成：
     - `stg_actual_wages.sql` - ステージングモデル
     - `mart_wage_trends.sql` - 産業別給与トレンド
     - `mart_gender_gap.sql` - 男女間賃金格差
     - `mart_employment_type_comparison.sql` - 一般 vs パート比較

3. **Looker Studioダッシュボード作成**
   - BigQuery接続
   - 時系列グラフ：給与・雇用・労働時間の推移
   - 産業別比較：横棒グラフ
   - 男女格差分析：ウォーターフォール図
   - フィルタ：産業、性別、就業形態、期間

### 6.2 中期的な改善
1. **Cloud Run化**
   - Dockerコンテナ化
   - Cloud Schedulerで月次実行
   - Secret ManagerでstatInfId管理

2. **Terraform化**
   - BigQueryデータセット・テーブル定義
   - Cloud Run Jobs設定
   - IAM権限管理

3. **データ拡張（Phase 2）**
   - 鉱工業指数の取得・処理
   - 在庫循環図の作成

### 6.3 長期的な展望
1. **Phase 3実装** - 家計調査データ
2. **機械学習予測** - 給与トレンドの予測モデル
3. **アラート機能** - 異常値検知（急激な給与減少等）

---

## 7. 技術スタック (Technology Stack)

### 現在使用中
- **言語**: Python 3.9+
- **ライブラリ**:
  - `pandas` - データ処理
  - `requests` - HTTP通信
  - `xlrd` - Excel読み込み
- **自動化**: GitHub Actions
- **バージョン管理**: Git
- **データ形式**: CSV（UTF-8 BOM付き）

### 今後導入予定
- **DWH**: BigQuery
- **変換**: dbt Core
- **BI**: Looker Studio
- **インフラ**: Terraform
- **コンテナ**: Docker
- **オーケストレーション**: Cloud Run Jobs + Cloud Scheduler

---

## 8. データソース (Data Sources)

### Phase 1（実装済み）
- **出典**: 厚生労働省「毎月勤労統計調査」
- **取得元**: e-Stat（政府統計の総合窓口）
- **URL**: https://www.e-stat.go.jp/
- **更新頻度**: 月次（毎月下旬に前月分確報公開）
- **データ期間**:
  - 指数データ: 1952年～現在（74年分）
  - 実数データ: 2024年1月～現在（23ヶ月分）
- **認証**: 不要（公開データの直接ダウンロード）

### Phase 2（未実装）
- **出典**: 経済産業省「鉱工業指数」
- **取得元**: e-Stat
- **更新頻度**: 月次

### Phase 3（未実装）
- **出典**: 総務省「家計調査」
- **取得元**: e-Stat
- **更新頻度**: 月次

---

## 9. 運用・保守 (Operations & Maintenance)

### 月次更新フロー
1. **自動実行**（毎月25日午前9時JST）
   - GitHub Actionsが指数データと実数データをダウンロード
   - 変更があれば自動コミット・プッシュ

2. **手動確認**（月1回）
   - 実数データのstatInfIdを更新（月次で変わる）
   - `src/extract/download_latest_actual_data.py`の85行目付近を編集
   - コミット・プッシュで次回から最新データ取得

3. **データ検証**
   - メタデータファイル（`data/metadata*.json`）で更新状況を確認
   - 行数・期間の整合性チェック

### エラーハンドリング
- GitHub Actionsで失敗時は自動的にIssue作成
- e-Statメンテナンス時は次回実行でリトライ
- statInfId変更時の手動対応手順をREADMEに記載

---

## 10. 制約事項・既知の問題 (Limitations & Known Issues)

### e-Stat API制約
- ❌ **API経由では最新データ取得不可**: 2014-2015年までのデータのみ
- ✅ **解決策**: 直接ダウンロードURL使用（statInfId + fileKind=4）

### 実数データの制約
- ⚠️ **statInfIdが月次で変わる**: 完全自動化には追加実装が必要
- ✅ **現在の対応**: 月1回の手動更新（5分程度）

### データ容量
- **実数データ（23ヶ月）**: 約10MB（Git除外）
- **指数データ（74年）**: 約40KB（Git管理）
- **マスターテーブル**: 約10KB（Git管理）

---

## Appendix: 参考資料

### 関連ドキュメント
- [データ構造ガイド](data/DATA_STRUCTURE.md)
- [マスターテーブル仕様](data/master/README.md)
- [クリーンデータ仕様](data/cleaned/README.md)
- [スクリプト説明](src/extract/README.md)

### 外部リンク
- [e-Stat 毎月勤労統計調査](https://www.e-stat.go.jp/stat-search/files?tstat=000001011791)
- [厚生労働省 毎月勤労統計調査](https://www.mhlw.go.jp/toukei/list/30-1.html)
- [BigQuery ドキュメント](https://cloud.google.com/bigquery/docs)
- [dbt ドキュメント](https://docs.getdbt.com/)

---

**最終更新**: 2026-01-28
**ステータス**: Phase 1 完了、Phase 2・3 未着手
**次のマイルストーン**: BigQueryへのデータロードとdbt変換の実装
