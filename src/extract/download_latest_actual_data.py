"""
e-Statから最新の毎勤原表（実数データ）を自動ダウンロードして処理する。

取得するデータ：
毎勤原表（令和7年11月確報以降の最新月）
- 現金給与総額（円）
- 産業別・就業形態別・性別

このスクリプトは定期実行（GitHub Actions等）で最新データを取得する。
"""

import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time


def download_estat_excel(stat_inf_id: str, output_dir: Path) -> Path:
    """
    e-Statから統計表Excelファイルをダウンロードする

    Args:
        stat_inf_id: 統計表ID
        output_dir: 保存先ディレクトリ

    Returns:
        ダウンロードしたファイルのパス
    """
    base_url = "https://www.e-stat.go.jp/stat-search/file-download"

    params = {
        "statInfId": stat_inf_id,
        "fileKind": 4  # Excel形式
    }

    print(f"  ダウンロード中: statInfId={stat_inf_id}")

    response = requests.get(base_url, params=params, timeout=60)
    response.raise_for_status()

    # ファイル保存
    output_path = output_dir / f"{stat_inf_id}.xls"
    with open(output_path, 'wb') as f:
        f.write(response.content)

    print(f"  ✓ ダウンロード完了: {output_path.name} ({len(response.content):,} bytes)")

    return output_path


def process_excel_to_dataframe(excel_path: Path, category_name: str) -> pd.DataFrame:
    """
    ダウンロードした毎勤原表Excelファイルを読み込んでDataFrameに変換する

    Args:
        excel_path: Excelファイルのパス
        category_name: カテゴリ名（ログ用）

    Returns:
        処理済みDataFrame
    """
    print(f"  Excelファイルを読み込み中: {excel_path.name}")

    try:
        # Excelファイルを読み込み（xlrdエンジン使用 - 古い.xls形式に対応）
        # ヘッダーなしで読み込み
        df = pd.read_excel(excel_path, sheet_name=0, engine='xlrd', header=None)

        print(f"  ✓ 読み込み完了: {len(df)}行 x {len(df.columns)}列")

        # 列名を設定（データ構造に基づく）
        column_names = [
            '産業コード',
            '性別',
            '就業形態',
            '常用労働者数_前調査期間末',
            '常用労働者数_本月増加',
            '常用労働者数_本月減少',
            '常用労働者数_本調査期間末',
            'パートタイム労働者数',
            '出勤日数',
            '実労働時間_総数',
            '実労働時間_所定内',
            '実労働時間_所定外',
            '現金給与_総額',
            '現金給与_きまって支給',
            '現金給与_所定内給与',
            '現金給与_超過労働給与',
            '現金給与_特別給与'
        ]

        # 最初の6行はヘッダー情報なのでスキップして、列名を設定
        df_data = df.iloc[6:].copy()  # 7行目からデータ開始
        df_data.columns = column_names

        # インデックスをリセット
        df_data = df_data.reset_index(drop=True)

        # 1行目の単位行（「円」など）を削除
        df_data = df_data.iloc[1:].copy()
        df_data = df_data.reset_index(drop=True)

        # 数値列を数値型に変換
        numeric_columns = [
            '常用労働者数_前調査期間末',
            '常用労働者数_本月増加',
            '常用労働者数_本月減少',
            '常用労働者数_本調査期間末',
            'パートタイム労働者数',
            '出勤日数',
            '実労働時間_総数',
            '実労働時間_所定内',
            '実労働時間_所定外',
            '現金給与_総額',
            '現金給与_きまって支給',
            '現金給与_所定内給与',
            '現金給与_超過労働給与',
            '現金給与_特別給与'
        ]

        for col in numeric_columns:
            # 数値に変換（エラーはNaNに）
            df_data[col] = pd.to_numeric(df_data[col], errors='coerce')

        # 全ての値がNaNの行を削除
        df_data = df_data.dropna(how='all', subset=numeric_columns)

        print(f"  ✓ データ整形完了: {len(df_data)}行")

        return df_data

    except Exception as e:
        print(f"  ✗ エラー: {e}")
        raise


def save_processed_data(df: pd.DataFrame, output_path: Path, category_name: str):
    """
    処理済みデータをCSVに保存する

    Args:
        df: DataFrame
        output_path: 出力ファイルパス
        category_name: カテゴリ名
    """
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"  ✓ 保存完了: {output_path}")
    print(f"    行数: {len(df):,}, 列数: {len(df.columns)}")


def main():
    print("=" * 100)
    print("毎月勤労統計調査 - 最新実数データ（毎勤原表）の自動取得")
    print("=" * 100)
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 取得する統計表の定義
    # 注: statInfIdは毎月更新されるため、最新のIDを使用する必要がある
    # 現在は2025年11月確報のIDを使用
    datasets = [
        {
            'stat_inf_id': '000040397563',
            'name': '毎勤原表（令和7年11月確報）',
            'output_filename': 'actual_wages_latest.csv'
        }
    ]

    # 作業ディレクトリの作成
    temp_dir = Path("data/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)

    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    # 各データセットを処理
    results = []

    for i, dataset in enumerate(datasets, 1):
        print(f"\n{i}/{len(datasets)}: {dataset['name']}")
        print("-" * 100)

        try:
            # ダウンロード
            excel_path = download_estat_excel(dataset['stat_inf_id'], temp_dir)

            # 少し待機（サーバー負荷軽減）
            time.sleep(1)

            # Excel読み込み
            df = process_excel_to_dataframe(excel_path, dataset['name'])

            # CSV保存
            output_path = output_dir / dataset['output_filename']
            save_processed_data(df, output_path, dataset['name'])

            results.append({
                'name': dataset['name'],
                'status': 'success',
                'output': output_path
            })

        except Exception as e:
            print(f"  ✗ エラー: {e}")
            results.append({
                'name': dataset['name'],
                'status': 'failed',
                'error': str(e)
            })

        print()

    # サマリー
    print("=" * 100)
    print("完了サマリー")
    print("=" * 100)
    print()

    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"取得成功: {success_count}/{len(results)}件")
    print()

    for result in results:
        status_icon = "✓" if result['status'] == 'success' else "✗"
        print(f"{status_icon} {result['name']}")

        if result['status'] == 'success':
            print(f"   保存先: {result['output']}")
        else:
            print(f"   エラー: {result['error']}")

    print()

    # メタデータファイルの作成（Pathオブジェクトを文字列に変換）
    metadata = {
        'last_updated': datetime.now().isoformat(),
        'data_type': 'actual_amounts',  # 実数データ
        'datasets': [
            {
                'name': r['name'],
                'status': r['status'],
                'output': str(r.get('output', '')),
                'error': r.get('error', '')
            }
            for r in results
        ]
    }

    import json
    metadata_path = output_dir / 'metadata_actual.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"メタデータ保存: {metadata_path}")
    print()

    if success_count == len(results):
        print("✓ 全データの取得に成功しました")
        print()
        print("【重要】")
        print("statInfIdは毎月更新されます。")
        print("最新月のデータを取得するには、e-Statから最新のstatInfIdを確認して")
        print("このスクリプトのdatasetsリストを更新してください。")
        return 0
    else:
        print(f"⚠ {len(results) - success_count}件のデータ取得に失敗しました")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
