"""
データファイルのカラム名を英文字化する。
"""

import pandas as pd
from pathlib import Path


def convert_actual_wages_columns(input_file: Path, output_file: Path):
    """
    実数データのカラム名を英文字化
    """
    print(f"処理中: {input_file.name}")

    # カラム名マッピング
    column_mapping = {
        '年月': 'year_month',
        '産業コード': 'industry_code',
        '性別': 'gender',
        '就業形態': 'employment_type',
        '常用労働者数_前調査期間末': 'regular_workers_prev',
        '常用労働者数_本月増加': 'regular_workers_increase',
        '常用労働者数_本月減少': 'regular_workers_decrease',
        '常用労働者数_本調査期間末': 'regular_workers_current',
        'パートタイム労働者数': 'parttime_workers',
        '出勤日数': 'working_days',
        '実労働時間_総数': 'total_working_hours',
        '実労働時間_所定内': 'scheduled_working_hours',
        '実労働時間_所定外': 'overtime_hours',
        '現金給与_総額': 'total_cash_earnings',
        '現金給与_きまって支給': 'scheduled_cash_earnings',
        '現金給与_所定内給与': 'contractual_cash_earnings',
        '現金給与_超過労働給与': 'overtime_pay',
        '現金給与_特別給与': 'special_cash_earnings'
    }

    # データ読み込み
    df = pd.read_csv(input_file)
    print(f"  元データ: {len(df):,}行 x {len(df.columns)}列")

    # カラム名を英文字化
    df = df.rename(columns=column_mapping)

    # 保存
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"  ✓ 英文字化完了: {output_file.name}")
    print(f"  保存データ: {len(df):,}行 x {len(df.columns)}列")
    print()

    return df


def convert_index_columns(input_file: Path, output_file: Path, index_type: str):
    """
    指数データのカラム名を英文字化

    指数データは特殊なヘッダー構造を持っているため、
    データ行のみを抽出して整形する
    """
    print(f"処理中: {input_file.name} ({index_type})")

    # ヘッダーなしで読み込み
    df = pd.read_csv(input_file, header=None)
    print(f"  元データ: {len(df):,}行 x {len(df.columns)}列")

    # データ行を抽出（10行目以降がデータ）
    df_data = df.iloc[10:].copy()

    # カラム名を設定
    column_names = ['year', 'jan', 'feb', 'mar', 'apr', 'may', 'jun',
                    'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

    # 必要な列数分のみカラム名を適用
    df_data = df_data.iloc[:, :len(column_names)]
    df_data.columns = column_names

    # 年列を整数型に変換（エラーは除外）
    df_data['year'] = pd.to_numeric(df_data['year'], errors='coerce')
    df_data = df_data.dropna(subset=['year'])
    df_data['year'] = df_data['year'].astype(int)

    # 月のデータを数値型に変換
    month_columns = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                     'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    for col in month_columns:
        df_data[col] = pd.to_numeric(df_data[col], errors='coerce')

    # インデックスをリセット
    df_data = df_data.reset_index(drop=True)

    # 保存
    df_data.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"  ✓ 英文字化完了: {output_file.name}")
    print(f"  保存データ: {len(df_data):,}行 x {len(df_data.columns)}列")
    print(f"  期間: {df_data['year'].min()}年 ～ {df_data['year'].max()}年")
    print()

    return df_data


def main():
    print("=" * 100)
    print("データファイルのカラム名英文字化")
    print("=" * 100)
    print()

    data_dir = Path("data")
    output_dir = Path("data/cleaned")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 実数データ（過去23ヶ月統合版）
    print("1. 実数データ（過去23ヶ月統合版）")
    print("-" * 100)
    convert_actual_wages_columns(
        data_dir / "actual_wages_historical.csv",
        output_dir / "actual_wages_historical.csv"
    )

    # 2. 実数データ（最新月）
    print("2. 実数データ（最新月）")
    print("-" * 100)
    convert_actual_wages_columns(
        data_dir / "actual_wages_latest.csv",
        output_dir / "actual_wages_latest.csv"
    )

    # 3. 指数データ（給与）
    print("3. 指数データ（現金給与総額指数）")
    print("-" * 100)
    convert_index_columns(
        data_dir / "wage_index_latest.csv",
        output_dir / "wage_index.csv",
        "wage"
    )

    # 4. 指数データ（雇用）
    print("4. 指数データ（常用雇用指数）")
    print("-" * 100)
    convert_index_columns(
        data_dir / "employment_index_latest.csv",
        output_dir / "employment_index.csv",
        "employment"
    )

    # 5. 指数データ（労働時間）
    print("5. 指数データ（総実労働時間指数）")
    print("-" * 100)
    convert_index_columns(
        data_dir / "hours_index_latest.csv",
        output_dir / "hours_index.csv",
        "hours"
    )

    print("=" * 100)
    print("✓ 全データファイルの英文字化が完了しました")
    print("=" * 100)
    print()
    print("保存先: data/cleaned/")
    print("  - actual_wages_historical.csv  : 実数データ（2024-01～2025-11）")
    print("  - actual_wages_latest.csv      : 実数データ（最新月のみ）")
    print("  - wage_index.csv               : 給与指数（1952～2025）")
    print("  - employment_index.csv         : 雇用指数（1952～2025）")
    print("  - hours_index.csv              : 労働時間指数（1952～2025）")
    print()


if __name__ == "__main__":
    main()
