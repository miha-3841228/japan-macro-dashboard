"""
マスターテーブル（データディクショナリ、コードマスター）を作成する。
"""

import pandas as pd
from pathlib import Path


def create_column_dictionary():
    """
    カラム定義のマスターテーブルを作成
    """

    # 実数データのカラム定義
    actual_columns = [
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '年月',
            'column_name_english': 'year_month',
            'data_type': 'VARCHAR(7)',
            'description': '調査年月（YYYY-MM形式）',
            'example': '2024-01'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '産業コード',
            'column_name_english': 'industry_code',
            'data_type': 'VARCHAR(10)',
            'description': '産業分類コード（T=全産業、0-9=産業分類番号）',
            'example': 'T, 0, 1, 3, 4, 5, 7, 9'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '性別',
            'column_name_english': 'gender',
            'data_type': 'VARCHAR(1)',
            'description': '性別（T=全体、M=男性、F=女性）',
            'example': 'T, M, F'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '就業形態',
            'column_name_english': 'employment_type',
            'data_type': 'VARCHAR(1)',
            'description': '就業形態（T=全体、N=一般労働者、P=パートタイム労働者）',
            'example': 'T, N, P'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '常用労働者数_前調査期間末',
            'column_name_english': 'regular_workers_prev',
            'data_type': 'INTEGER',
            'description': '前調査期間末の常用労働者数（人）',
            'example': '51770535'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '常用労働者数_本月増加',
            'column_name_english': 'regular_workers_increase',
            'data_type': 'INTEGER',
            'description': '本月中の常用労働者数増加（人）',
            'example': '822731'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '常用労働者数_本月減少',
            'column_name_english': 'regular_workers_decrease',
            'data_type': 'INTEGER',
            'description': '本月中の常用労働者数減少（人）',
            'example': '729613'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '常用労働者数_本調査期間末',
            'column_name_english': 'regular_workers_current',
            'data_type': 'INTEGER',
            'description': '本調査期間末の常用労働者数（人）',
            'example': '51863653'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': 'パートタイム労働者数',
            'column_name_english': 'parttime_workers',
            'data_type': 'INTEGER',
            'description': 'パートタイム労働者数（人）',
            'example': '16333991'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '出勤日数',
            'column_name_english': 'working_days',
            'data_type': 'DECIMAL(4,1)',
            'description': '1人平均月間出勤日数（日）',
            'example': '17.4'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '実労働時間_総数',
            'column_name_english': 'total_working_hours',
            'data_type': 'DECIMAL(5,1)',
            'description': '1人平均月間総実労働時間数（時間）',
            'example': '134.8'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '実労働時間_所定内',
            'column_name_english': 'scheduled_working_hours',
            'data_type': 'DECIMAL(5,1)',
            'description': '1人平均月間所定内労働時間数（時間）',
            'example': '124.8'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '実労働時間_所定外',
            'column_name_english': 'overtime_hours',
            'data_type': 'DECIMAL(5,1)',
            'description': '1人平均月間所定外労働時間数（時間）',
            'example': '10.0'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '現金給与_総額',
            'column_name_english': 'total_cash_earnings',
            'data_type': 'INTEGER',
            'description': '1人平均月間現金給与総額（円）',
            'example': '313531'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '現金給与_きまって支給',
            'column_name_english': 'scheduled_cash_earnings',
            'data_type': 'INTEGER',
            'description': 'きまって支給する給与（円）',
            'example': '290616'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '現金給与_所定内給与',
            'column_name_english': 'contractual_cash_earnings',
            'data_type': 'INTEGER',
            'description': '所定内給与額（円）',
            'example': '269754'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '現金給与_超過労働給与',
            'column_name_english': 'overtime_pay',
            'data_type': 'INTEGER',
            'description': '超過労働給与額（円）',
            'example': '20862'
        },
        {
            'table_name': 'actual_wages',
            'column_name_japanese': '現金給与_特別給与',
            'column_name_english': 'special_cash_earnings',
            'data_type': 'INTEGER',
            'description': '特別に支払われた給与（賞与等）（円）',
            'example': '22915'
        }
    ]

    # 指数データのカラム定義
    index_columns = [
        {
            'table_name': 'wage_index',
            'column_name_japanese': '年',
            'column_name_english': 'year',
            'data_type': 'INTEGER',
            'description': '調査年',
            'example': '2025'
        },
        {
            'table_name': 'wage_index',
            'column_name_japanese': '1月',
            'column_name_english': 'jan',
            'data_type': 'DECIMAL(6,2)',
            'description': '1月の指数（2020年=100）',
            'example': '101.5'
        },
        {
            'table_name': 'wage_index',
            'column_name_japanese': '2月',
            'column_name_english': 'feb',
            'data_type': 'DECIMAL(6,2)',
            'description': '2月の指数（2020年=100）',
            'example': '102.3'
        },
        {
            'table_name': 'wage_index',
            'column_name_japanese': '3月',
            'column_name_english': 'mar',
            'data_type': 'DECIMAL(6,2)',
            'description': '3月の指数（2020年=100）',
            'example': '103.1'
        },
        {
            'table_name': 'wage_index',
            'column_name_japanese': '4月',
            'column_name_english': 'apr',
            'data_type': 'DECIMAL(6,2)',
            'description': '4月の指数（2020年=100）',
            'example': '100.8'
        },
        {
            'table_name': 'wage_index',
            'column_name_japanese': '5月',
            'column_name_english': 'may',
            'data_type': 'DECIMAL(6,2)',
            'description': '5月の指数（2020年=100）',
            'example': '99.9'
        },
        {
            'table_name': 'wage_index',
            'column_name_japanese': '6月',
            'column_name_english': 'jun',
            'data_type': 'DECIMAL(6,2)',
            'description': '6月の指数（2020年=100）',
            'example': '100.2'
        },
        {
            'table_name': 'wage_index',
            'column_name_japanese': '7月',
            'column_name_english': 'jul',
            'data_type': 'DECIMAL(6,2)',
            'description': '7月の指数（2020年=100）',
            'example': '101.7'
        },
        {
            'table_name': 'wage_index',
            'column_name_japanese': '8月',
            'column_name_english': 'aug',
            'data_type': 'DECIMAL(6,2)',
            'description': '8月の指数（2020年=100）',
            'example': '99.5'
        },
        {
            'table_name': 'wage_index',
            'column_name_japanese': '9月',
            'column_name_english': 'sep',
            'data_type': 'DECIMAL(6,2)',
            'description': '9月の指数（2020年=100）',
            'example': '100.4'
        },
        {
            'table_name': 'wage_index',
            'column_name_japanese': '10月',
            'column_name_english': 'oct',
            'data_type': 'DECIMAL(6,2)',
            'description': '10月の指数（2020年=100）',
            'example': '101.1'
        },
        {
            'table_name': 'wage_index',
            'column_name_japanese': '11月',
            'column_name_english': 'nov',
            'data_type': 'DECIMAL(6,2)',
            'description': '11月の指数（2020年=100）',
            'example': '102.0'
        },
        {
            'table_name': 'wage_index',
            'column_name_japanese': '12月',
            'column_name_english': 'dec',
            'data_type': 'DECIMAL(6,2)',
            'description': '12月の指数（2020年=100）',
            'example': '104.5'
        }
    ]

    df_columns = pd.DataFrame(actual_columns + index_columns)
    return df_columns


def create_industry_master():
    """
    産業コードマスターを作成
    """
    industries = [
        {
            'industry_code': 'T',
            'industry_name_japanese': '調査産業計',
            'industry_name_english': 'All industries surveyed',
            'major_category': None,
            'display_order': 0
        },
        {
            'industry_code': '0',
            'industry_name_japanese': '鉱業，採石業，砂利採取業',
            'industry_name_english': 'Mining and quarrying of stone and gravel',
            'major_category': '第二次産業',
            'display_order': 1
        },
        {
            'industry_code': '1',
            'industry_name_japanese': '建設業',
            'industry_name_english': 'Construction',
            'major_category': '第二次産業',
            'display_order': 2
        },
        {
            'industry_code': '3',
            'industry_name_japanese': '製造業',
            'industry_name_english': 'Manufacturing',
            'major_category': '第二次産業',
            'display_order': 3
        },
        {
            'industry_code': '4',
            'industry_name_japanese': '電気・ガス・熱供給・水道業',
            'industry_name_english': 'Electricity, gas, heat supply and water',
            'major_category': '第二次産業',
            'display_order': 4
        },
        {
            'industry_code': '5',
            'industry_name_japanese': '情報通信業',
            'industry_name_english': 'Information and communications',
            'major_category': '第三次産業',
            'display_order': 5
        },
        {
            'industry_code': '7',
            'industry_name_japanese': '運輸業，郵便業',
            'industry_name_english': 'Transport and postal activities',
            'major_category': '第三次産業',
            'display_order': 6
        },
        {
            'industry_code': '9',
            'industry_name_japanese': '卸売業，小売業',
            'industry_name_english': 'Wholesale and retail trade',
            'major_category': '第三次産業',
            'display_order': 7
        }
    ]

    df_industries = pd.DataFrame(industries)
    return df_industries


def create_gender_master():
    """
    性別マスターを作成
    """
    genders = [
        {
            'gender_code': 'T',
            'gender_name_japanese': '男女計',
            'gender_name_english': 'Total (Male and Female)',
            'display_order': 0
        },
        {
            'gender_code': 'M',
            'gender_name_japanese': '男性',
            'gender_name_english': 'Male',
            'display_order': 1
        },
        {
            'gender_code': 'F',
            'gender_name_japanese': '女性',
            'gender_name_english': 'Female',
            'display_order': 2
        }
    ]

    df_genders = pd.DataFrame(genders)
    return df_genders


def create_employment_type_master():
    """
    就業形態マスターを作成
    """
    employment_types = [
        {
            'employment_type_code': 'T',
            'employment_type_name_japanese': '一般・パート計',
            'employment_type_name_english': 'Total (Regular and Part-time)',
            'display_order': 0
        },
        {
            'employment_type_code': 'N',
            'employment_type_name_japanese': '一般労働者',
            'employment_type_name_english': 'Regular workers',
            'display_order': 1
        },
        {
            'employment_type_code': 'P',
            'employment_type_name_japanese': 'パートタイム労働者',
            'employment_type_name_english': 'Part-time workers',
            'display_order': 2
        }
    ]

    df_employment_types = pd.DataFrame(employment_types)
    return df_employment_types


def main():
    print("=" * 100)
    print("マスターテーブルの作成")
    print("=" * 100)
    print()

    output_dir = Path("data/master")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. カラム定義マスター
    print("1. カラム定義マスターを作成中...")
    df_columns = create_column_dictionary()
    output_path = output_dir / "column_dictionary.csv"
    df_columns.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"   ✓ 保存完了: {output_path}")
    print(f"     - 実数データ: {len([x for x in df_columns['table_name'] if x == 'actual_wages'])}カラム")
    print(f"     - 指数データ: {len([x for x in df_columns['table_name'] if x == 'wage_index'])}カラム")
    print()

    # 2. 産業コードマスター
    print("2. 産業コードマスターを作成中...")
    df_industries = create_industry_master()
    output_path = output_dir / "industry_master.csv"
    df_industries.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"   ✓ 保存完了: {output_path}")
    print(f"     - 産業数: {len(df_industries)}件")
    print()

    # 3. 性別マスター
    print("3. 性別マスターを作成中...")
    df_genders = create_gender_master()
    output_path = output_dir / "gender_master.csv"
    df_genders.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"   ✓ 保存完了: {output_path}")
    print(f"     - 性別数: {len(df_genders)}件")
    print()

    # 4. 就業形態マスター
    print("4. 就業形態マスターを作成中...")
    df_employment_types = create_employment_type_master()
    output_path = output_dir / "employment_type_master.csv"
    df_employment_types.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"   ✓ 保存完了: {output_path}")
    print(f"     - 就業形態数: {len(df_employment_types)}件")
    print()

    print("=" * 100)
    print("✓ マスターテーブルの作成が完了しました")
    print("=" * 100)
    print()
    print("保存先: data/master/")
    print("  - column_dictionary.csv        : カラム定義マスター")
    print("  - industry_master.csv          : 産業コードマスター")
    print("  - gender_master.csv            : 性別マスター")
    print("  - employment_type_master.csv   : 就業形態マスター")
    print()


if __name__ == "__main__":
    main()
