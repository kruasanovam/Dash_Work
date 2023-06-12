import requests
import pandas as pd
import numpy as np
import time
from Dash_Work.backend.data.bq_actions import *
from Dash_Work.backend.api.job_details_api import *
from Dash_Work.backend.api.all_jobs_api import *

from Dash_Work.params import *
from google.cloud import bigquery
import base64
import csv
import random
from retrying import retry

### Supress SSL certificate warnings when ssl_verify=False
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@retry(wait_exponential_multiplier=10000, wait_exponential_max=120000)
def get_jwt():
    """fetch the jwt token object"""
    URL = 'https://rest.arbeitsagentur.de/oauth/gettoken_cc'

    headers = {
        'User-Agent': 'Jobsuche/2.9.2 (de.arbeitsagentur.jobboerse; build:1077; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    }

    data = {
      'client_id': 'c003a37f-024f-462a-b36d-b001be4cd24a',
      'client_secret': '32a39620-32b3-4307-9aa1-511e3d7f48a8',
      'grant_type': 'client_credentials'
    }

    print ("🧚‍♀️ Trying to get authorisation token to connect to the API...")
    response = requests.post(URL, headers=headers, data=data, verify=False)

    if response.status_code == 200:
        print(f"✅ Auth token received!")
        print(f'New token: {response.json()["access_token"]}')
    elif response.status_code in [401, 403]:
        print (response.status_code)
        print ("Maybe token is expired? Trying with a new token")
        headers['OAuthAccessToken'] = get_jwt()
        print(response.json())
        response = requests.get(url=URL, headers=headers, verify=False)
    else:
        print ("Something is wrong...here is the response:")
        print (response.status_code)
        print (response.content)

    return response.json()["access_token"]


def get_all_job_details():

    table_name = 'all_jobs'
    print(f"👀 Fetching list of job ids from BQ!")
    job_refs = download_table_from_bg(table_name)
    print(f"✅List of job ids downloaded from BQ! Total number or jobs = {len(job_refs)}")
    all_details = []
    jwt = get_jwt()
    start_time = time.time()
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    save_rage = np.arange(1000, 2000000, 1000).tolist()
    num = 0
    num_jobs = len(job_refs)
    for ref in job_refs:
        print(f"👀 Fetching job ref {ref}. Only {(num_jobs-num)} jobs left 🤞🤞🤞")
        job_detail_api_result = get_job_detail(jwt, ref)
        job_detail = job_detail_api_result[0]
        if job_detail_api_result[1]:
            jwt = get_jwt()
            job_detail = job_detail_api_result[0]
        all_details.append([
                            job_detail.get("refnr", None),
                            job_detail.get("aktuelleVeroeffentlichungsdatum", None),
                            job_detail.get("arbeitgeber", None),
                            job_detail.get("branche", None),
                            job_detail.get("branchengruppe", None),
                            job_detail.get("arbeitsorte", [{"ort":None}])[0].get("ort", None),
                            job_detail.get("arbeitsorte", [{"plz":None}])[0].get("plz", None),
                            job_detail.get("arbeitsorte", [{"land":None}])[0].get("land", None),
                            job_detail.get("arbeitszeitmodelle", None),
                            job_detail.get("befristung", None),
                            job_detail.get("betriebsgroesse", None),
                            job_detail.get("eintrittsdatum", None),
                            job_detail.get("ersteVeroeffentlichungsdatum", None),
                            job_detail.get("titel", None),
                            job_detail.get("beruf", None),
                            job_detail.get("stellenbeschreibung", None),
                            job_detail.get("tarifvertrag", None),
                            job_detail.get("arbeitgeberdarstellung", None),
                            job_detail.get("istPrivateArbeitsvermittlung", None),
                            job_detail.get("istZeitarbeit", None)
                             ])
        if num in save_rage:
            df = pd.DataFrame(all_details)
            df.columns = ["refnr", "aktuelleVeroeffentlichungsdatum","arbeitgeber","branche","branchengruppe",
                      "arbeitsorte_ort", "arbeitsorte_plz", "arbeitsorte_land", "arbeitszeitmodelle",
                      "befristung", "betriebsgroesse", "eintrittsdatum", "ersteVeroeffentlichungsdatum",
                      "titel", "beruf", "stellenbeschreibung", "tarifvertrag", "arbeitgeberdarstellung",
                      "istPrivateArbeitsvermittlung", "istZeitarbeit"
                      ]
            file_path = f"{LOCAL_DATA_PATH_JOB_DETAILS}/job_details_{timestamp}.csv"
            save_df_to_csv(df, file_path)
        num+=1
    print("✅✅✅ DONE for ALL jobs", df.shape)
    print("--- %s seconds ---" % (time.time() - start_time))

def save_df_to_csv(df, file_path):
    try:
        df.to_csv(file_path)
        print(f"✅ Saved jobs to {file_path}. Data size =", df.shape)
    except UnicodeEncodeError as e:
        print(f"UnicodeEncodeError when saving df to csv file {str(e)}. List of unsaved jobs: {df['refnr']}")
    except:
        print(f"Something else when saving df to csv file. List of unsaved jobs: {df['refnr']}")

if __name__ == "__main__":
    pass
