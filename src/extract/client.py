"""
e-Stat API Client for fetching Japanese government statistics.

This module provides a client class to interact with the e-Stat API
and retrieve statistical data for economic analysis.
"""

import os
from typing import Optional, Dict, Any, List
import requests
import pandas as pd
from dataclasses import dataclass


@dataclass
class StatConfig:
    """Configuration for statistical data retrieval."""
    stats_data_id: str
    cd_cat01: Optional[str] = None
    cd_time: Optional[str] = None
    limit: int = 100000


class EStatAPIClient:
    """
    Client for interacting with the e-Stat API.

    e-Stat is the Japanese government's portal for official statistics.
    This client provides methods to fetch and process statistical data.

    Attributes:
        api_key: API key for e-Stat authentication
        base_url: Base URL for e-Stat API endpoints
    """

    BASE_URL = "https://api.e-stat.go.jp/rest/3.0/app/json"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the e-Stat API client.

        Args:
            api_key: e-Stat API key. If not provided, reads from ESTAT_API_KEY env var.

        Raises:
            ValueError: If API key is not provided or found in environment.
        """
        self.api_key = api_key or os.getenv("ESTAT_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide via argument or ESTAT_API_KEY env var."
            )
        self.session = requests.Session()

    def get_stats_data(
        self,
        config: StatConfig,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch statistical data from e-Stat API.

        Args:
            config: Configuration object specifying which data to retrieve
            **kwargs: Additional query parameters for the API

        Returns:
            JSON response from the API as a dictionary

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        endpoint = f"{self.BASE_URL}/getStatsData"

        params = {
            "appId": self.api_key,
            "statsDataId": config.stats_data_id,
            "limit": config.limit,
        }

        # Add optional parameters if provided
        if config.cd_cat01:
            params["cdCat01"] = config.cd_cat01
        if config.cd_time:
            params["cdTime"] = config.cd_time

        # Merge additional parameters
        params.update(kwargs)

        response = self.session.get(endpoint, params=params)
        response.raise_for_status()

        # Debug: Print response details if JSON parsing might fail
        try:
            return response.json()
        except ValueError as e:
            print(f"DEBUG: Failed to parse JSON response")
            print(f"DEBUG: Status Code: {response.status_code}")
            print(f"DEBUG: Response Text: {response.text[:500]}")
            raise ValueError(f"Invalid JSON response from API: {e}")

    def get_stats_list(
        self,
        search_word: Optional[str] = None,
        stats_code: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search for available statistical datasets.

        Args:
            search_word: Keyword to search for
            stats_code: Statistical survey code
            limit: Maximum number of results

        Returns:
            JSON response containing list of available datasets
        """
        endpoint = f"{self.BASE_URL}/getStatsList"

        params = {
            "appId": self.api_key,
            "limit": limit,
        }

        if search_word:
            params["searchWord"] = search_word
        if stats_code:
            params["statsCode"] = stats_code

        response = self.session.get(endpoint, params=params)
        response.raise_for_status()

        return response.json()

    def json_to_dataframe(self, json_response: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert e-Stat API JSON response to pandas DataFrame.

        Args:
            json_response: JSON response from get_stats_data()

        Returns:
            DataFrame containing the statistical data

        Raises:
            KeyError: If JSON structure is unexpected
            ValueError: If data cannot be converted to DataFrame
        """
        # Extract the data section from the response
        result = json_response.get("GET_STATS_DATA", {}).get("STATISTICAL_DATA", {})
        data_inf = result.get("DATA_INF", {})
        values = data_inf.get("VALUE", [])

        if not values:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(values)

        return df

    def fetch_and_transform(self, config: StatConfig) -> pd.DataFrame:
        """
        Fetch data from API and transform to DataFrame in one call.

        Args:
            config: Configuration for data retrieval

        Returns:
            DataFrame containing the fetched and transformed data
        """
        json_data = self.get_stats_data(config)
        df = self.json_to_dataframe(json_data)

        return df

    def close(self):
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Example usage
if __name__ == "__main__":
    # Example: Fetch Monthly Labour Survey data
    client = EStatAPIClient()

    config = StatConfig(
        stats_data_id="0003410379",  # Example: Monthly Labour Survey
        limit=1000
    )

    try:
        df = client.fetch_and_transform(config)
        print(f"Fetched {len(df)} rows")
        print(df.head())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
