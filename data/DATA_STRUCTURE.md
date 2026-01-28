# データ構造ガイド

## ディレクトリ構成

```
data/
├── cleaned/                          # 英文字カラム名のクリーンデータ（推奨）
│   ├── actual_wages_historical.csv   # 実数データ（2024-01～2025-11）
│   ├── actual_wages_latest.csv       # 実数データ（最新月のみ）
│   ├── wage_index.csv                # 給与指数（1952～2025）
│   ├── employment_index.csv          # 雇用指数（1952～2025）
│   ├── hours_index.csv               # 労働時間指数（1952～2025）
│   └── README.md                     # クリーンデータの詳細説明
│
├── master/                           # マスターテーブル（コードと名称の対応）
│   ├── column_dictionary.csv         # カラム定義マスター（31カラム）
│   ├── industry_master.csv           # 産業コードマスター（8産業）
│   ├── gender_master.csv             # 性別マスター（3区分）
│   ├── employment_type_master.csv    # 就業形態マスター（3区分）
│   └── README.md                     # マスターテーブルの詳細説明
│
├── actual_wages_historical.csv       # 元データ（日本語カラム名）
├── actual_wages_latest.csv           # 元データ（日本語カラム名）
├── wage_index_latest.csv             # 元データ（日本語カラム名）
├── employment_index_latest.csv       # 元データ（日本語カラム名）
├── hours_index_latest.csv            # 元データ（日本語カラム名）
│
├── metadata.json                     # 指数データのメタ情報
├── metadata_actual.json              # 最新実数データのメタ情報
├── metadata_actual_historical.json   # 過去実数データのメタ情報
│
└── DATA_STRUCTURE.md                 # このファイル
```

## データファイルの使い分け

### 分析用途別の推奨ファイル

| 分析目的 | 使用ファイル | 理由 |
|---------|-------------|------|
| SQL/BigQueryでの分析 | `cleaned/` 配下 | 英文字カラム名でクエリが書きやすい |
| Python/Pandasでの分析 | `cleaned/` または元データ | どちらでも可 |
| 可視化ツール（Looker Studio等） | `cleaned/` 配下 | 英文字カラム名で設定が簡単 |
| 元データの確認 | 元データ（ルート） | 日本語カラム名で直感的 |

### データセット別の推奨ファイル

| 分析シナリオ | 推奨ファイル | データ量 |
|------------|-------------|---------|
| 直近2年間の詳細給与分析 | `cleaned/actual_wages_historical.csv` | 99,765行 |
| 最新月のスナップショット | `cleaned/actual_wages_latest.csv` | 4,355行 |
| 70年超の長期トレンド分析 | `cleaned/wage_index.csv` | 147行 |
| 産業別の比較分析 | `cleaned/actual_wages_historical.csv` + `master/industry_master.csv` | - |
| 男女間格差の分析 | `cleaned/actual_wages_historical.csv` + `master/gender_master.csv` | - |

## データ関連図

```
┌─────────────────────────────────────────────────────────────────┐
│                      cleaned/ (分析用データ)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  actual_wages_historical.csv                                    │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ year_month | industry_code | gender | employment_type│      │
│  │ 2024-01    | T            | T      | T               │      │
│  │ 2024-01    | 3            | M      | N               │      │
│  └──────────────────────────────────────────────────────┘      │
│         │              │           │            │               │
│         └──────┬───────┴───────┬───┴────────┬──┘               │
│                │               │            │                   │
│        ┌───────▼──────┐ ┌──────▼─────┐ ┌───▼─────────┐       │
│        │industry_master│ │gender_master│ │employment_  │       │
│        │              │ │            │ │type_master  │       │
│        │              │ │            │ │             │       │
│        │ T: 調査産業計│ │ T: 男女計  │ │ T: 全体     │       │
│        │ 3: 製造業    │ │ M: 男性    │ │ N: 一般     │       │
│        │ 5: 情報通信業│ │ F: 女性    │ │ P: パート   │       │
│        └──────────────┘ └────────────┘ └─────────────┘       │
│                                                                 │
│  wage_index.csv / employment_index.csv / hours_index.csv        │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ year | jan | feb | mar | ... | nov | dec             │      │
│  │ 2024 | 2.8 | 2.3 | 3.4 | ... | 1.6 | 2.0             │      │
│  │ 2025 | NaN | 2.2 | NaN | ... | 2.0 | 1.4             │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    master/ (参照マスター)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  column_dictionary.csv                                          │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ table_name | column_name_english | data_type | ...    │      │
│  │ actual_wages | year_month | VARCHAR(7) | ...          │      │
│  │ actual_wages | industry_code | VARCHAR(10) | ...      │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## クイックスタートガイド

### 1. BigQueryにロードする

```bash
# マスターテーブルのロード
bq load --source_format=CSV --skip_leading_rows=1 \
  dataset.industry_master \
  data/master/industry_master.csv

bq load --source_format=CSV --skip_leading_rows=1 \
  dataset.gender_master \
  data/master/gender_master.csv

bq load --source_format=CSV --skip_leading_rows=1 \
  dataset.employment_type_master \
  data/master/employment_type_master.csv

# 実数データのロード
bq load --source_format=CSV --skip_leading_rows=1 \
  dataset.actual_wages_historical \
  data/cleaned/actual_wages_historical.csv

# 指数データのロード
bq load --source_format=CSV --skip_leading_rows=1 \
  dataset.wage_index \
  data/cleaned/wage_index.csv
```

### 2. Pythonで分析する

```python
import pandas as pd

# 実数データの読み込み
df_wages = pd.read_csv('data/cleaned/actual_wages_historical.csv')

# マスターテーブルの読み込み
df_industry = pd.read_csv('data/master/industry_master.csv')
df_gender = pd.read_csv('data/master/gender_master.csv')

# 産業名を付与
df_merged = df_wages.merge(
    df_industry,
    on='industry_code',
    how='left'
)

# 2025年11月の産業別平均給与
result = df_merged[
    (df_merged['year_month'] == '2025-11') &
    (df_merged['gender'] == 'T') &
    (df_merged['employment_type'] == 'T')
].groupby('industry_name_japanese')['total_cash_earnings'].mean()

print(result.sort_values(ascending=False))
```

### 3. SQLで分析する（BigQuery例）

```sql
-- 産業別・男女別の給与推移
SELECT
    a.year_month,
    i.industry_name_japanese,
    g.gender_name_japanese,
    AVG(a.total_cash_earnings) as avg_earnings
FROM `project.dataset.actual_wages_historical` a
LEFT JOIN `project.dataset.industry_master` i
    ON a.industry_code = i.industry_code
LEFT JOIN `project.dataset.gender_master` g
    ON a.gender = g.gender_code
WHERE a.employment_type = 'T'
  AND a.industry_code IS NOT NULL
GROUP BY a.year_month, i.industry_name_japanese, g.gender_name_japanese
ORDER BY a.year_month, i.display_order, g.display_order;
```

## データ更新フロー

```
1. 元データ取得
   ├─ download_latest_indices.py        → 指数データ（月1回自動）
   ├─ download_latest_actual_data.py    → 実数データ最新月（月1回手動）
   └─ download_historical_actual_data.py → 実数データ過去分（必要時）
           ↓
2. マスターテーブル作成（初回のみ）
   └─ create_master_tables.py
           ↓
3. カラム名英文字化
   └─ convert_to_english_columns.py
           ↓
4. 分析用データ完成
   ├─ data/cleaned/
   └─ data/master/
```

## データ品質メモ

### NULL値の扱い

- **実数データ**: 性別・産業コードがNULLの行は「小計行」（特定の集計レベル）
- **指数データ**: データが存在しない年月はNULL

### コード体系

- **T**: Total（合計・全体）
- **数字（0,1,3,4,5,7,9）**: 産業分類番号（日本標準産業分類に準拠）
- **M/F**: Male/Female
- **N/P**: Normal workers / Part-time workers

### データソース

- **出典**: 厚生労働省「毎月勤労統計調査」
- **取得元**: e-Stat（政府統計の総合窓口）
- **更新頻度**: 月次（毎月下旬に前月分確報公開）

## 詳細ドキュメント

- クリーンデータの詳細: `data/cleaned/README.md`
- マスターテーブルの詳細: `data/master/README.md`
- データ取得方法: `src/extract/README.md`
