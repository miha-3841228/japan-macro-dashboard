# マスターテーブル

このディレクトリには、データの意味を理解し、SQLでの結合に使用するためのマスターテーブルが含まれています。

## マスターテーブル一覧

### 1. column_dictionary.csv（カラム定義マスター）

全データファイルのカラム定義を記載したデータディクショナリ。

**カラム構成:**
- `table_name`: テーブル名（actual_wages, wage_index等）
- `column_name_japanese`: 日本語カラム名
- `column_name_english`: 英語カラム名（SQL用）
- `data_type`: データ型
- `description`: カラムの説明
- `example`: 値の例

**用途:**
- カラム名の対応表として参照
- データ型の確認
- SQLテーブル作成時のスキーマ定義

**SQLでの利用例:**
```sql
-- 実数データのカラム一覧を取得
SELECT
    column_name_english,
    column_name_japanese,
    data_type,
    description
FROM column_dictionary
WHERE table_name = 'actual_wages'
ORDER BY column_name_english;
```

---

### 2. industry_master.csv（産業コードマスター）

産業分類コードとその名称を定義。

**カラム構成:**
- `industry_code`: 産業コード（T, 0, 1, 3, 4, 5, 7, 9）
- `industry_name_japanese`: 産業名（日本語）
- `industry_name_english`: 産業名（英語）
- `major_category`: 大分類（第二次産業/第三次産業）
- `display_order`: 表示順序

**産業コード一覧:**

| コード | 産業名 | 大分類 |
|-------|--------|--------|
| T | 調査産業計 | - |
| 0 | 鉱業，採石業，砂利採取業 | 第二次産業 |
| 1 | 建設業 | 第二次産業 |
| 3 | 製造業 | 第二次産業 |
| 4 | 電気・ガス・熱供給・水道業 | 第二次産業 |
| 5 | 情報通信業 | 第三次産業 |
| 7 | 運輸業，郵便業 | 第三次産業 |
| 9 | 卸売業，小売業 | 第三次産業 |

**SQLでの利用例:**
```sql
-- 産業名を含めた給与データの取得
SELECT
    a.year_month,
    i.industry_name_japanese,
    i.major_category,
    a.total_cash_earnings
FROM actual_wages_historical a
LEFT JOIN industry_master i ON a.industry_code = i.industry_code
WHERE a.year_month = '2025-11'
  AND a.gender = 'T'
  AND a.employment_type = 'T'
ORDER BY i.display_order;
```

---

### 3. gender_master.csv（性別マスター）

性別コードとその名称を定義。

**カラム構成:**
- `gender_code`: 性別コード（T, M, F）
- `gender_name_japanese`: 性別名（日本語）
- `gender_name_english`: 性別名（英語）
- `display_order`: 表示順序

**性別コード一覧:**

| コード | 性別名 |
|-------|--------|
| T | 男女計 |
| M | 男性 |
| F | 女性 |

**SQLでの利用例:**
```sql
-- 性別名を含めた給与データの取得
SELECT
    a.year_month,
    g.gender_name_japanese,
    AVG(a.total_cash_earnings) as avg_earnings
FROM actual_wages_historical a
LEFT JOIN gender_master g ON a.gender = g.gender_code
WHERE a.industry_code = 'T'
  AND a.employment_type = 'T'
GROUP BY a.year_month, g.gender_name_japanese, g.display_order
ORDER BY a.year_month, g.display_order;
```

---

### 4. employment_type_master.csv（就業形態マスター）

就業形態コードとその名称を定義。

**カラム構成:**
- `employment_type_code`: 就業形態コード（T, N, P）
- `employment_type_name_japanese`: 就業形態名（日本語）
- `employment_type_name_english`: 就業形態名（英語）
- `display_order`: 表示順序

**就業形態コード一覧:**

| コード | 就業形態名 |
|-------|-----------|
| T | 一般・パート計 |
| N | 一般労働者 |
| P | パートタイム労働者 |

**SQLでの利用例:**
```sql
-- 就業形態別の給与比較
SELECT
    a.year_month,
    e.employment_type_name_japanese,
    AVG(a.total_cash_earnings) as avg_earnings,
    AVG(a.total_working_hours) as avg_hours
FROM actual_wages_historical a
LEFT JOIN employment_type_master e ON a.employment_type = e.employment_type_code
WHERE a.industry_code = 'T'
  AND a.gender = 'T'
GROUP BY a.year_month, e.employment_type_name_japanese, e.display_order
ORDER BY a.year_month, e.display_order;
```

---

## 全マスターを使った複合クエリ例

```sql
-- 産業別・性別・就業形態別の詳細レポート
SELECT
    a.year_month,
    i.industry_name_japanese,
    i.major_category,
    g.gender_name_japanese,
    e.employment_type_name_japanese,
    a.total_cash_earnings,
    a.total_working_hours,
    a.regular_workers_current
FROM actual_wages_historical a
LEFT JOIN industry_master i ON a.industry_code = i.industry_code
LEFT JOIN gender_master g ON a.gender = g.gender_code
LEFT JOIN employment_type_master e ON a.employment_type = e.employment_type_code
WHERE a.year_month = '2025-11'
  AND a.industry_code IS NOT NULL
ORDER BY
    i.display_order,
    g.display_order,
    e.display_order;
```

## BigQueryでのテーブル作成例

```sql
-- 産業コードマスターテーブル
CREATE TABLE `project.dataset.industry_master` (
  industry_code STRING,
  industry_name_japanese STRING,
  industry_name_english STRING,
  major_category STRING,
  display_order INT64
);

-- 性別マスターテーブル
CREATE TABLE `project.dataset.gender_master` (
  gender_code STRING,
  gender_name_japanese STRING,
  gender_name_english STRING,
  display_order INT64
);

-- 就業形態マスターテーブル
CREATE TABLE `project.dataset.employment_type_master` (
  employment_type_code STRING,
  employment_type_name_japanese STRING,
  employment_type_name_english STRING,
  display_order INT64
);

-- 実数データテーブル
CREATE TABLE `project.dataset.actual_wages_historical` (
  year_month STRING,
  industry_code STRING,
  gender STRING,
  employment_type STRING,
  regular_workers_prev INT64,
  regular_workers_increase INT64,
  regular_workers_decrease INT64,
  regular_workers_current INT64,
  parttime_workers INT64,
  working_days FLOAT64,
  total_working_hours FLOAT64,
  scheduled_working_hours FLOAT64,
  overtime_hours FLOAT64,
  total_cash_earnings INT64,
  scheduled_cash_earnings INT64,
  contractual_cash_earnings INT64,
  overtime_pay INT64,
  special_cash_earnings INT64
);
```

## メンテナンス

マスターテーブルは基本的に固定ですが、以下の場合に更新が必要です：

1. **産業分類の変更**: 日本標準産業分類の改訂時
2. **新しい指標の追加**: データソースに新しいカラムが追加された場合
3. **データ型の変更**: より適切なデータ型が判明した場合

更新時は `src/extract/create_master_tables.py` を編集して再実行してください。
