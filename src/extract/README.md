# 毎月勤労統計調査データ自動取得システム

## 概要

このシステムは、e-Statから毎月勤労統計調査の以下のデータを自動的にダウンロードして処理します：

1. **指数データ**: 長期時系列（1952年～最新月）- トレンド分析に最適
2. **実数データ**: 金額ベース（円単位）- 詳細な給与水準の分析に最適

## データの使い分け

### 指数データを使う場合

- 長期的なトレンド分析（1952年～）
- 季節調整済みの推移を見たい
- 異なる時期の相対的な変化を比較したい
- 基準年（2020年）を100とした変化率で分析したい

### 実数データを使う場合

- 実際の給与金額（円）を知りたい
- 産業別・性別・就業形態別の詳細な比較をしたい
- 最新の給与水準を分析したい
- 直近2年間（2024-2025年）のデータで十分な場合

## 取得データ

### 指数データ（長期時系列）

| データ名 | statInfId | ファイル名 |
|---------|-----------|-----------|
| 現金給与総額指数 | 000032189720 | `data/wage_index_latest.csv` |
| 常用雇用指数 | 000032189714 | `data/employment_index_latest.csv` |
| 総実労働時間指数 | 000032189742 | `data/hours_index_latest.csv` |

- **基準年**: 2020年=100
- **データ期間**: 1952年～最新月（2026年1月時点で2025年11月まで）
- **データ構造**: 166行 x 21列（年×月のマトリクス形式）

### 実数データ（毎勤原表）

| データ名 | 期間 | ファイル名 |
|---------|------|-----------|
| 毎勤原表（最新月） | 2025年11月 | `data/actual_wages_latest.csv` |
| 毎勤原表（過去23ヶ月） | 2024年1月～2025年11月 | `data/actual_wages_historical.csv` |

- **単位**: 円
- **データ構造**:
  - 最新月: 4,355行 x 17列
  - 過去23ヶ月統合版: 99,765行 x 18列（年月列含む）
- **主要指標**: 現金給与総額、きまって支給する給与、所定内給与、超過労働給与、特別給与
- **分類**: 産業別・性別・就業形態別
- **注意**: statInfIdは毎月更新されます

## 自動更新スケジュール

GitHub Actionsにより、**毎月25日午前9時（JST）**に自動的に実行されます。

最新データが取得できた場合、自動的にコミット・プッシュされます。

## スクリプト一覧

### データ取得スクリプト

| スクリプト | 説明 | 実行頻度 |
|-----------|------|---------|
| `download_latest_indices.py` | 指数データ取得（1952～最新月） | 月1回（自動） |
| `download_latest_actual_data.py` | 実数データ取得（最新月のみ） | 月1回（手動） |
| `download_historical_actual_data.py` | 実数データ過去分取得（2024-01～） | 必要時 |

### データ処理スクリプト

| スクリプト | 説明 | 実行頻度 |
|-----------|------|---------|
| `create_master_tables.py` | マスターテーブル作成 | 初回のみ |
| `convert_to_english_columns.py` | カラム名英文字化 | データ更新時 |

### 基盤モジュール

| ファイル | 説明 |
|---------|------|
| `client.py` | e-Stat APIクライアント |

## 手動実行方法

### ローカルで実行

```bash
# 依存パッケージのインストール
pip install requests pandas xlrd

# 指数データの取得（1952年～最新月の長期時系列）
python download_latest_indices.py

# 実数データの取得（最新月のみ）
python download_latest_actual_data.py

# 実数データの過去分一括取得（2024年1月～2025年11月）
python download_historical_actual_data.py

# マスターテーブル作成（初回のみ）
python create_master_tables.py

# カラム名英文字化（データ取得後に実行）
python convert_to_english_columns.py
```

**重要**: 実数データの取得には、最新のstatInfIdが必要です。

#### 最新月データの更新手順

毎月、以下の手順でstatInfIdを更新してください：

1. [e-Stat 毎勤原表ページ](https://www.e-stat.go.jp/stat-search/files?toukei=00450071&tstat=000001011791&tclass1=000001164732&layout=dataset)にアクセス
2. 最新月の「毎勤原表（令和○年○月確報）」を探す
3. URLの`stat_infid=`パラメータからstatInfIdを取得
4. `src/extract/download_latest_actual_data.py`の`datasets`リストを更新

#### 過去データの更新手順

新しい月のデータを追加する場合：

1. 上記ページで最新月のstatInfIdを確認
2. `src/extract/download_historical_actual_data.py`の`datasets`リストに追加
3. スクリプトを再実行すると、新しい月を含む統合ファイルが生成されます

### GitHub Actionsで手動実行

1. GitHubリポジトリの「Actions」タブを開く
2. 「Update Labour Survey Data」ワークフローを選択
3. 「Run workflow」ボタンをクリック

## 技術詳細

### データ取得方法

e-Stat APIではなく、**直接ファイルダウンロードURL**を使用しています。

```
https://www.e-stat.go.jp/stat-search/file-download?statInfId={統計表ID}&fileKind=4
```

- `fileKind=4`: Excel形式（.xls）
- **認証不要**: 公開データのため、APIキー不要でダウンロード可能
- **最新データ**: e-Stat APIは2014-2015年までしか対応していないため、この方法を採用

### なぜe-Stat APIを使わないのか？

e-Stat APIには2つのID体系があります：

- **statsDataId** (API用): 2014-2015年までのデータのみ
- **statInfId** (Webダウンロード用): 2025年までの最新データ

APIでは最新データが取得できないため、直接ダウンロード方式を採用しました。

## トラブルシューティング

### ワークフローが失敗した場合

自動的にGitHub Issueが作成されます。以下を確認してください：

1. e-Statサイトがメンテナンス中でないか
2. 統計表IDが変更されていないか
3. ファイル形式が変更されていないか（.xls → .xlsx等）

### 実数データのstatInfIdエラー

実数データ（毎勤原表）のstatInfIdは**毎月変わります**。以下の手順で更新してください：

1. [e-Stat 毎勤原表ページ](https://www.e-stat.go.jp/stat-search/files?toukei=00450071&tstat=000001011791&tclass1=000001164732&layout=dataset)で最新月のデータを確認
2. 最新の「毎勤原表（令和○年○月確報）」のstatInfIdを取得
3. `src/extract/download_latest_actual_data.py`の85行目付近の`datasets`リストを更新：

```python
datasets = [
    {
        'stat_inf_id': '000040XXXXXX',  # ← 最新のstatInfIdに更新
        'name': '毎勤原表（令和○年○月確報）',
        'output_filename': 'actual_wages_latest.csv'
    }
]
```

4. 変更をコミット・プッシュすると、次回のワークフロー実行時に最新データが取得されます

### データ形式が変わった場合

- 指数データ: `src/extract/download_latest_indices.py`の`process_excel_to_dataframe()`関数を修正
- 実数データ: `src/extract/download_latest_actual_data.py`の`process_excel_to_dataframe()`関数を修正

## データファイル構成

取得後の`data/`ディレクトリ構成：

```
data/
├── wage_index_latest.csv          # 現金給与総額指数（1952年～2025年11月）
├── employment_index_latest.csv    # 常用雇用指数（1952年～2025年11月）
├── hours_index_latest.csv         # 総実労働時間指数（1952年～2025年11月）
├── actual_wages_latest.csv        # 毎勤原表・最新月（2025年11月）
├── actual_wages_historical.csv    # 毎勤原表・過去23ヶ月統合版（2024-01～2025-11）
├── metadata.json                  # 指数データのメタ情報
├── metadata_actual.json           # 最新実数データのメタ情報
└── metadata_actual_historical.json # 過去実数データのメタ情報
```

## メタデータ

更新日時やステータスは各メタデータファイルに記録されています：

**指数データ（`metadata.json`）:**
```json
{
  "last_updated": "2026-01-28T10:30:00.123456",
  "datasets": [
    {
      "name": "現金給与総額指数",
      "status": "success",
      "output": "data/wage_index_latest.csv"
    }
  ]
}
```

**実数データ（`metadata_actual_historical.json`）:**
```json
{
  "last_updated": "2026-01-28T22:34:00.123456",
  "data_type": "actual_amounts_historical",
  "period": "2024-01 to 2025-11",
  "total_months": 23,
  "success_count": 23,
  "total_rows": 99765,
  "output_file": "actual_wages_historical.csv"
}
```
