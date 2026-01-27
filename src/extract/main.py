"""
Main entry point for extracting data from e-Stat API.

This script fetches data from the Monthly Labour Survey (毎月勤労統計調査)
and displays the results.
"""

import sys
from pathlib import Path

# Add parent directory to path to import client module
sys.path.append(str(Path(__file__).parent))

from client import EStatAPIClient, StatConfig
from dotenv import load_dotenv


def main():
    """
    Fetch Monthly Labour Survey data from e-Stat API and display results.
    """
    # Load environment variables from .env file
    load_dotenv()

    print("=" * 60)
    print("e-Stat API Data Extraction - Monthly Labour Survey")
    print("=" * 60)

    try:
        # Initialize the API client
        print("\n[1] Initializing e-Stat API client...")
        with EStatAPIClient() as client:
            # Configure the data to fetch
            # statsDataId='0003008391' - Monthly Labour Survey (毎月勤労統計調査)
            config = StatConfig(
                stats_data_id="0003008391",
                limit=1000
            )

            print(f"[2] Fetching data (statsDataId={config.stats_data_id})...")

            # Fetch and transform data
            df = client.fetch_and_transform(config)

            # Display results
            print(f"\n[3] Successfully fetched {len(df)} rows")
            print(f"    Columns: {len(df.columns)}")
            print("\n" + "=" * 60)
            print("First 5 rows of the data:")
            print("=" * 60)
            print(df.head())

            # Display column names
            print("\n" + "=" * 60)
            print("Available columns:")
            print("=" * 60)
            for idx, col in enumerate(df.columns, 1):
                print(f"  {idx}. {col}")

    except ValueError as e:
        print(f"\n[ERROR] Configuration error: {e}")
        print("\nPlease ensure ESTAT_API_KEY is set in your .env file:")
        print("  ESTAT_API_KEY=your_api_key_here")
        sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] Failed to fetch data: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Extraction completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
