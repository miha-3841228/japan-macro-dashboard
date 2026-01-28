# クリーンデータ（英文字カラム名）

このディレクトリには、SQLで扱いやすいように英文字化されたカラム名のデータファイルが含まれています。

## データファイル

### 実数データ（金額ベース・円単位）

#### `actual_wages_historical.csv`
- **期間**: 2024年1月～2025年11月（23ヶ月）
- **行数**: 99,765行
- **列数**: 18列
- **説明**: 産業別・性別・就業形態別の月次給与実績データ

#### `actual_wages_latest.csv`
- **期間**: 2025年11月（最新月のみ）
- **行数**: 4,355行
- **列数**: 17列
- **説明**: 最新月の詳細データ

**主要カラム:**
- `year_month`: 調査年月（YYYY-MM形式）
- `industry_code`: 産業コード（T, 0, 1, 3, 4, 5, 7, 9）
- `gender`: 性別（T=全体, M=男性, F=女性）
- `employment_type`: 就業形態（T=全体, N=一般, P=パート）
- `total_cash_earnings`: 現金給与総額（円）
- `scheduled_cash_earnings`: きまって支給する給与（円）
- `contractual_cash_earnings`: 所定内給与（円）
- `overtime_pay`: 超過労働給与（円）
- `special_cash_earnings`: 特別給与（円）
- `total_working_hours`: 総実労働時間（時間）
- `overtime_hours`: 所定外労働時間（時間）
- `regular_workers_current`: 常用労働者数（人）

### 指数データ（長期時系列・2020年=100）

#### `wage_index.csv`
- **期間**: 1952年～2025年（74年間）
- **行数**: 147行
- **列数**: 13列（year + 12ヶ月）
- **説明**: 現金給与総額指数の長期トレンド

#### `employment_index.csv`
- **期間**: 1952年～2025年（74年間）
- **行数**: 147行
- **列数**: 13列（year + 12ヶ月）
- **説明**: 常用雇用指数の長期トレンド

#### `hours_index.csv`
- **期間**: 1952年～2025年（74年間）
- **行数**: 147行
- **列数**: 13列（year + 12ヶ月）
- **説明**: 総実労働時間指数の長期トレンド

**カラム:**
- `year`: 年
- `jan`, `feb`, `mar`, `apr`, `may`, `jun`, `jul`, `aug`, `sep`, `oct`, `nov`, `dec`: 各月の指数値

## SQLでの利用例

### 実数データのクエリ例

```sql
-- 2024-2025年の産業別平均給与
SELECT
    industry_code,
    AVG(total_cash_earnings) as avg_earnings
FROM actual_wages_historical
WHERE employment_type = 'T'  -- 全体
  AND gender = 'T'           -- 男女計
GROUP BY industry_code
ORDER BY avg_earnings DESC;

-- 男女間の給与格差分析
SELECT
    year_month,
    industry_code,
    MAX(CASE WHEN gender = 'M' THEN total_cash_earnings END) as male_earnings,
    MAX(CASE WHEN gender = 'F' THEN total_cash_earnings END) as female_earnings,
    MAX(CASE WHEN gender = 'M' THEN total_cash_earnings END) -
    MAX(CASE WHEN gender = 'F' THEN total_cash_earnings END) as gender_gap
FROM actual_wages_historical
WHERE employment_type = 'T'
  AND industry_code = 'T'
GROUP BY year_month, industry_code
ORDER BY year_month;

-- 一般労働者 vs パートタイム労働者の比較
SELECT
    year_month,
    MAX(CASE WHEN employment_type = 'N' THEN total_cash_earnings END) as regular_earnings,
    MAX(CASE WHEN employment_type = 'P' THEN total_cash_earnings END) as parttime_earnings,
    ROUND(MAX(CASE WHEN employment_type = 'P' THEN total_cash_earnings END) * 100.0 /
          MAX(CASE WHEN employment_type = 'N' THEN total_cash_earnings END), 2) as parttime_ratio
FROM actual_wages_historical
WHERE industry_code = 'T'
  AND gender = 'T'
GROUP BY year_month
ORDER BY year_month;
```

### 指数データのクエリ例

```sql
-- 長期トレンド分析（年次平均）
SELECT
    year,
    ROUND((jan + feb + mar + apr + may + jun +
           jul + aug + sep + oct + nov + dec) / 12.0, 2) as annual_avg_index
FROM wage_index
WHERE year >= 2000
ORDER BY year;

-- 前年同月比の算出
SELECT
    w1.year,
    ROUND((w1.jan - w0.jan) * 100.0 / w0.jan, 2) as jan_yoy,
    ROUND((w1.feb - w0.feb) * 100.0 / w0.feb, 2) as feb_yoy,
    ROUND((w1.mar - w0.mar) * 100.0 / w0.mar, 2) as mar_yoy
FROM wage_index w1
LEFT JOIN wage_index w0 ON w1.year = w0.year + 1
WHERE w1.year >= 2020
ORDER BY w1.year;
```

### マスターテーブルとのJOIN例

```sql
-- 産業名を含めた給与データ
SELECT
    a.year_month,
    i.industry_name_japanese,
    i.industry_name_english,
    g.gender_name_japanese,
    e.employment_type_name_japanese,
    a.total_cash_earnings
FROM actual_wages_historical a
LEFT JOIN industry_master i ON a.industry_code = i.industry_code
LEFT JOIN gender_master g ON a.gender = g.gender_code
LEFT JOIN employment_type_master e ON a.employment_type = e.employment_type_code
WHERE a.year_month = '2025-11'
  AND a.industry_code IS NOT NULL
  AND a.gender = 'T'
  AND a.employment_type = 'T'
ORDER BY a.total_cash_earnings DESC;
```

## データ型定義

### actual_wages_historical / actual_wages_latest

| カラム名 | データ型 | NULL許可 | 説明 |
|---------|---------|---------|------|
| year_month | VARCHAR(7) | NO | 調査年月 |
| industry_code | VARCHAR(10) | YES | 産業コード |
| gender | VARCHAR(1) | YES | 性別 |
| employment_type | VARCHAR(1) | YES | 就業形態 |
| regular_workers_prev | INTEGER | YES | 前調査期間末の常用労働者数 |
| regular_workers_increase | INTEGER | YES | 本月増加数 |
| regular_workers_decrease | INTEGER | YES | 本月減少数 |
| regular_workers_current | INTEGER | YES | 本調査期間末の常用労働者数 |
| parttime_workers | INTEGER | YES | パートタイム労働者数 |
| working_days | DECIMAL(4,1) | YES | 出勤日数 |
| total_working_hours | DECIMAL(5,1) | YES | 総実労働時間 |
| scheduled_working_hours | DECIMAL(5,1) | YES | 所定内労働時間 |
| overtime_hours | DECIMAL(5,1) | YES | 所定外労働時間 |
| total_cash_earnings | INTEGER | YES | 現金給与総額 |
| scheduled_cash_earnings | INTEGER | YES | きまって支給する給与 |
| contractual_cash_earnings | INTEGER | YES | 所定内給与 |
| overtime_pay | INTEGER | YES | 超過労働給与 |
| special_cash_earnings | INTEGER | YES | 特別給与 |

### wage_index / employment_index / hours_index

| カラム名 | データ型 | NULL許可 | 説明 |
|---------|---------|---------|------|
| year | INTEGER | NO | 年 |
| jan | DECIMAL(6,2) | YES | 1月の指数 |
| feb | DECIMAL(6,2) | YES | 2月の指数 |
| mar | DECIMAL(6,2) | YES | 3月の指数 |
| apr | DECIMAL(6,2) | YES | 4月の指数 |
| may | DECIMAL(6,2) | YES | 5月の指数 |
| jun | DECIMAL(6,2) | YES | 6月の指数 |
| jul | DECIMAL(6,2) | YES | 7月の指数 |
| aug | DECIMAL(6,2) | YES | 8月の指数 |
| sep | DECIMAL(6,2) | YES | 9月の指数 |
| oct | DECIMAL(6,2) | YES | 10月の指数 |
| nov | DECIMAL(6,2) | YES | 11月の指数 |
| dec | DECIMAL(6,2) | YES | 12月の指数 |

## 関連ファイル

マスターテーブルの詳細は `data/master/` ディレクトリを参照してください：
- `column_dictionary.csv`: 全カラムの詳細定義
- `industry_master.csv`: 産業コード一覧
- `gender_master.csv`: 性別コード一覧
- `employment_type_master.csv`: 就業形態コード一覧
