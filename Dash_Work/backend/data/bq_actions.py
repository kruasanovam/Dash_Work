import pandas as pd
from colorama import Fore, Style
from google.cloud import bigquery
from Dash_Work.params import *
import csv
import time
from retrying import retry


def save_dataframe_to_bq(
        data: pd.DataFrame,
        gcp_project:str,
        bq_dataset:str,
        table: str,
        truncate: bool
    ) -> None:
    """
    - Save the DataFrame to BigQuery
    - Empty the table beforehand if `truncate` is True, append otherwise
    """

    assert isinstance(data, pd.DataFrame)
    full_table_name = f"{gcp_project}.{bq_dataset}.{table}"
    print(Fore.BLUE + f"\nSave data to BigQuery @ {full_table_name}...:" + Style.RESET_ALL)

    # Load data onto full_table_name
    data.columns = [f"_{column}" if not str(column)[0].isalpha() and not str(column)[0] == "_" else str(column) for column in data.columns]

    client = bigquery.Client()

    # Define write mode and schema
    write_mode = "WRITE_TRUNCATE" if truncate else "WRITE_APPEND"
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

    print(f"\n{'Write' if truncate else 'Append'} {full_table_name} ({data.shape[0]} rows)")

    # Load data
    job = client.load_table_from_dataframe(data, full_table_name, job_config=job_config)
    result = job.result()  # wait for the job to complete

    print(f"✅ Data saved to bigquery, with shape {data.shape}")


def download_table_from_bg(table_name):

    query = f"""
        SELECT {"refnr"}
        FROM {GCP_PROJECT}.{BQ_DATASET}.{table_name}
        """
    client = bigquery.Client(project=GCP_PROJECT)
    query_job = client.query(query)
    result = query_job.result()
    list = result.to_dataframe().values.flatten().tolist()

    return list


def get_latest_arbeitsort_list():
    print ("Getting list of latest valid arbeitsorts...")
    with open(f"{LOCAL_DATA_PATH_VALID_ORTS}/orts.csv", newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    f.close()
    ort_list = []
    for ort in data:
        ort_list.append(ort[0])
    return ort_list


def join_tables_from_bq():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    #tables = get_table_names_from_bq()
    query = f"""
        SELECT *
        FROM {GCP_PROJECT}.{BQ_DATASET}.all_jobs_details_20230609_075553_copy as job_details
        FULL OUTER JOIN {GCP_PROJECT}.{BQ_DATASET}.all_jobs_20230609_014055 as all_jobs
        ON job_details.refnr = all_jobs.refnr
        """
    client = bigquery.Client(project=GCP_PROJECT)

    query_job = client.query(query)
    result = query_job.result()
    df = result.to_dataframe()
    df.to_csv(f"{LOCAL_DATA_PATH}/master_{timestamp}.csv")
    print("✅✅✅ Merged all tables and saved to file 'master_all_data.csv'. Data size =", df.shape)

    save_dataframe_to_bq(
            df,
            gcp_project=GCP_PROJECT,
            bq_dataset=BQ_DATASET,
            table=f'master_{timestamp}',
            truncate=True
        )
    print("✅✅✅ Uploaded dataframe to Big Query")


if __name__ == "__main__":
    pass
