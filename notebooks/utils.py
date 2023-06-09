import pandas as pd

from google.cloud import bigquery
from colorama import Fore, Style
from pathlib import Path
import os


def get_data_with_cache(
        query:str,
        data_has_header=True
    ) -> pd.DataFrame:
    """
    Retrieve `query` data from BigQuery, or from `cache_path` if the file exists
    Store at `cache_path` if retrieved from BigQuery for future use
    """
    print(Fore.BLUE + "\nLoad data from BigQuery server..." + Style.RESET_ALL)
    client = bigquery.Client(project=os.environ.get("GCP_PROJECT"))
    query_job = client.query(query)
    result = query_job.result()
    df = result.to_dataframe()

    return df
