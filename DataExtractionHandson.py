import pandas as pd
import os
from dotenv import load_dotenv
import sys
import requests
import logging
load_dotenv()
API_URL = os.getenv("API_URL")
csv_path = os.getenv("CSV_FILE_PATH")

logging.basicConfig (
    level=logging.INFO,
    format = '%(asctime)s -%(levelname)s - %(message)s',
    handlers = [logging.StreamHandler(sys.stdout)]
)
# Extracting data from an API
def extract_API_data(url: str) -> pd.DataFrame | None | str :
    logging.info("Attempting API Extraction")
    try:
        response =requests.get(url)
        print(type(response))
        response.raise_for_status()
        data= response.json()
        if not data:
            logging.warning("Api call success but no data")
            return None
        datadf = pd.DataFrame(data)
        datadf['calculation'] = datadf['id']*2
        logging.info(f"data converted to Dataframe\n{datadf.tail()}")
        save_data_url = r"D:\samples\api_data.csv"
        # save_data_file_name ='api_data.csv'
        # finalurl=os.path.join(save_data_url,save_data_file_name)
        print(f"finalurl : {save_data_url}")
        datadf.to_csv(save_data_url,index=False,mode='x',header=False)
        return datadf

    except Exception as error:
        logging.error(f"errors founds in extracting data from the API:{error}")

# For private API we need to pass api_key also to the requests method
'''
api_key =os.getenv("API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}",  # We can Adjust as per API documentation (e.g., "Token {api_key}")
    "Content-Type": "application/json"     # May be required depending on the API
}
response =requests.get(api_url,headers)
'''

# Data Extraction from a CSV file

def load_csv_data(filepath: str) -> pd.DataFrame | None:
    logging.info(f"Attempting to extract data from a CSV file")
    try:
        logging.info(f"Checking if the file exists")
        print(filepath)
        if not os.path.exists(filepath):
            logging.error(f"File not found in the path: {filepath}")
            return None
        csv_data=pd.read_csv(filepath)
        if csv_data.empty:
            logging.warning(f"CSV File found but no data ")
            return None
        print(csv_data.head())
        return csv_data


    except Exception as error:
        logging.error("Error found while extracting data from the CSV: {error}")


extract_API_data(API_URL)
load_csv_data(csv_path)