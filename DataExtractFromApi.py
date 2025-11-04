import pandas as pd
import requests
from dotenv import load_dotenv
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
API_KEY = os.getenv("API_KEY")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")
API_URL = os.getenv("API_URL")
FREE_API_URL = "https://jsonplaceholder.typicode.com/posts" # A free, dummy API for demonstration

# --- Data Extraction Functions ---

def fetch_data_from_api(url: str) -> pd.DataFrame | None:
    """
    Fetches data from a specified API endpoint and returns a DataFrame.
    Returns None if the API call fails or no data is found.
    """
    logging.info(f"Attempting to fetch data from API: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        if not data:
            logging.warning("API call successful, but no data was returned.")
            return None

        return pd.DataFrame(data)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from API: {e}")
        return None
    except ValueError as e:
        logging.error(f"Error decoding JSON from API response: {e}")
        return None
if __name__ == "__main__":
    result = fetch_data_from_api(API_URL)
    if result is not None:
        logging.info(f"Api data fetched:\n{result.describe()}")
    else:
        logging.info(f"Some error in extraction")
