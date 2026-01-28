"""
e-Statから過去の毎勤原表（実数データ）を一括ダウンロードして統合する。

取得期間：2024年1月～2025年11月（23ヶ月分）
"""

import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time


def download_estat_excel(stat_inf_id: str, year_month: str, output_dir: Path) -> Path:
    """
    e-Statから統計表Excelファイルをダウンロードする

    Args:
        stat_inf_id: 統計表ID
        year_month: 年月（例: 2024-01）
        output_dir: 保存先ディレクトリ

    Returns:
        ダウンロードしたファイルのパス
    """
    base_url = "https://www.e-stat.go.jp/stat-search/file-download"

    params = {
        "statInfId": stat_inf_id,
        "fileKind": 4  # Excel形式
    }

    print(f"  ダウンロード中: {year_month}")

    response = requests.get(base_url, params=params, timeout=60)
    response.raise_for_status()

    # ファイル保存
    output_path = output_dir / f"{year_month}_{stat_inf_id}.xls"
    with open(output_path, 'wb') as f:
        f.write(response.content)

    print(f"  ✓ ダウンロード完了: {output_path.name} ({len(response.content):,} bytes)")

    return output_path


def process_excel_to_dataframe(excel_path: Path, year_month: str) -> pd.DataFrame:
    """
    ダウンロードした毎勤原表Excelファイルを読み込んでDataFrameに変換する

    Args:
        excel_path: Excelファイルのパス
        year_month: 年月（例: 2024-01）

    Returns:
        処理済みDataFrame
    """
    try:
        # Excelファイルを読み込み（xlrdエンジン使用 - 古い.xls形式に対応）
        df = pd.read_excel(excel_path, sheet_name=0, engine='xlrd', header=None)

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

        # 年月列を追加
        df_data.insert(0, '年月', year_month)

        return df_data

    except Exception as e:
        print(f"  ✗ エラー: {e}")
        raise


def main():
    print("=" * 100)
    print("毎月勤労統計調査 - 過去実数データ（毎勤原表）の一括取得")
    print("=" * 100)
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 取得する統計表の定義（2024年1月～2025年11月）
    datasets = [
        {'year_month': '2025-11', 'stat_inf_id': '000040397563', 'name': '令和7年11月確報'},
        {'year_month': '2025-10', 'stat_inf_id': '000040388924', 'name': '令和7年10月確報'},
        {'year_month': '2025-09', 'stat_inf_id': '000040370407', 'name': '令和7年9月確報'},
        {'year_month': '2025-08', 'stat_inf_id': '000040360166', 'name': '令和7年8月確報'},
        {'year_month': '2025-07', 'stat_inf_id': '000040323699', 'name': '令和7年7月確報'},
        {'year_month': '2025-06', 'stat_inf_id': '000040307886', 'name': '令和7年6月確報'},
        {'year_month': '2025-05', 'stat_inf_id': '000040298090', 'name': '令和7年5月確報'},
        {'year_month': '2025-04', 'stat_inf_id': '000040286506', 'name': '令和7年4月確報'},
        {'year_month': '2025-03', 'stat_inf_id': '000040279686', 'name': '令和7年3月確報'},
        {'year_month': '2025-02', 'stat_inf_id': '000040271186', 'name': '令和7年2月確報'},
        {'year_month': '2025-01', 'stat_inf_id': '000040269547', 'name': '令和7年1月確報'},
        {'year_month': '2024-12', 'stat_inf_id': '000040250081', 'name': '2024年12月確報'},
        {'year_month': '2024-11', 'stat_inf_id': '000040241981', 'name': '2024年11月確報'},
        {'year_month': '2024-10', 'stat_inf_id': '000040235081', 'name': '2024年10月確報'},
        {'year_month': '2024-09', 'stat_inf_id': '000040225606', 'name': '2024年9月確報'},
        {'year_month': '2024-08', 'stat_inf_id': '000040217309', 'name': '2024年8月確報'},
        {'year_month': '2024-07', 'stat_inf_id': '000040211461', 'name': '2024年7月確報'},
        {'year_month': '2024-06', 'stat_inf_id': '000040200080', 'name': '2024年6月確報'},
        {'year_month': '2024-05', 'stat_inf_id': '000040193700', 'name': '2024年5月確報'},
        {'year_month': '2024-04', 'stat_inf_id': '000040187736', 'name': '2024年4月確報'},
        {'year_month': '2024-03', 'stat_inf_id': '000040182381', 'name': '2024年3月確報'},
        {'year_month': '2024-02', 'stat_inf_id': '000040176301', 'name': '2024年2月確報'},
        {'year_month': '2024-01', 'stat_inf_id': '000040173518', 'name': '2024年1月確報'},
    ]

    print(f"取得期間: 2024年1月～2025年11月（{len(datasets)}ヶ月分）")
    print()

    # 作業ディレクトリの作成
    temp_dir = Path("data/temp_historical")
    temp_dir.mkdir(parents=True, exist_ok=True)

    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    # 各データセットを処理
    all_dataframes = []
    results = []

    for i, dataset in enumerate(datasets, 1):
        print(f"\n{i}/{len(datasets)}: {dataset['name']} ({dataset['year_month']})")
        print("-" * 100)

        try:
            # ダウンロード
            excel_path = download_estat_excel(
                dataset['stat_inf_id'],
                dataset['year_month'],
                temp_dir
            )

            # 少し待機（サーバー負荷軽減）
            time.sleep(0.5)

            # Excel読み込み
            df = process_excel_to_dataframe(excel_path, dataset['year_month'])
            print(f"  ✓ データ整形完了: {len(df)}行")

            all_dataframes.append(df)

            results.append({
                'year_month': dataset['year_month'],
                'name': dataset['name'],
                'status': 'success',
                'rows': len(df)
            })

        except Exception as e:
            print(f"  ✗ エラー: {e}")
            results.append({
                'year_month': dataset['year_month'],
                'name': dataset['name'],
                'status': 'failed',
                'error': str(e)
            })

    # 全データを統合
    print()
    print("=" * 100)
    print("データ統合中...")
    print("=" * 100)
    print()

    if all_dataframes:
        # 全DataFrameを結合
        combined_df = pd.concat(all_dataframes, ignore_index=True)

        # 年月でソート（古い順）
        combined_df = combined_df.sort_values('年月').reset_index(drop=True)

        # CSV保存
        output_path = output_dir / 'actual_wages_historical.csv'
        combined_df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"✓ 統合データ保存完了: {output_path}")
        print(f"  総行数: {len(combined_df):,}")
        print(f"  総列数: {len(combined_df.columns)}")
        print(f"  期間: {combined_df['年月'].min()} ～ {combined_df['年月'].max()}")
        print()

    # サマリー
    print("=" * 100)
    print("完了サマリー")
    print("=" * 100)
    print()

    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"取得成功: {success_count}/{len(results)}ヶ月")
    print()

    if success_count > 0:
        print("✓ 取得成功:")
        for result in results:
            if result['status'] == 'success':
                print(f"  - {result['year_month']}: {result['rows']:,}行")

    failed_count = len(results) - success_count
    if failed_count > 0:
        print()
        print("✗ 取得失敗:")
        for result in results:
            if result['status'] == 'failed':
                print(f"  - {result['year_month']}: {result['error']}")

    # メタデータファイルの作成
    metadata = {
        'last_updated': datetime.now().isoformat(),
        'data_type': 'actual_amounts_historical',
        'period': '2024-01 to 2025-11',
        'total_months': len(datasets),
        'success_count': success_count,
        'failed_count': failed_count,
        'total_rows': len(combined_df) if all_dataframes else 0,
        'output_file': 'actual_wages_historical.csv'
    }

    import json
    metadata_path = output_dir / 'metadata_actual_historical.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print()
    print(f"メタデータ保存: {metadata_path}")
    print()

    if success_count == len(results):
        print("✓ 全データの取得に成功しました")
        return 0
    elif success_count > 0:
        print(f"⚠ {failed_count}ヶ月のデータ取得に失敗しました")
        return 1
    else:
        print("✗ 全てのデータ取得に失敗しました")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
