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

    response = requests.post(URL, headers=headers, data=data, verify=False)
    print ("🧚‍♀️ Trying to get authorisation token to connect to the API...")

    if response.status_code != 200:
        if response.status_code in [401, 403]:
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



def get_all_jobs(places):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    page_size= 100
    umkreis = 0
    all_jobs = []
    jwt = get_jwt()
    print(f"✅ Auth token received!")

    places = places
    save_rage = np.arange(10000, 2000000, 10000).tolist()
    num = 1

    for place in places:
        branches = get_branches_per_arbeitsort(jwt, place, umkreis=umkreis)

        place_jobs = []
        for branche in branches:
            page_jobs = True
            page = 1
            while page_jobs:
                page_jobs = search_jobs(jwt, arbeitsort=place, umkreis=umkreis, branche=branche,
                                page=page, page_size=page_size).get("stellenangebote", [])
                if page_jobs:
                    print(f"👀 Downloading jobs for place {place} and branche {branche} from page {page}...")
                    place_jobs.extend(page_jobs)
                    page += 1

        if place_jobs:
            all_jobs.extend(place_jobs)

            if num in save_rage:
                place_df = pd.json_normalize(place_jobs)
                print(f"✅ Downloaded all jobs for place {place}. Data size =", place_df.shape)
                df = pd.json_normalize(all_jobs,sep='_')
                df.to_csv(f"{LOCAL_DATA_PATH_ALL_JOBS}/all_jobs_{timestamp}.csv")
                print(f"✅✅Saved {num} jobs and saved to file 'all_jobs_{timestamp}.csv'. Data size =", df.shape)
        num += 1

    return df

def get_jobs_and_load_to_bg():

    all_places = get_latest_arbeitsort_list()
    start_time = time.time()
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    data = get_all_jobs(places=all_places)
    table_name = f'raw_all_jobs_{timestamp}'
    save_dataframe_to_bq(
            data,
            gcp_project=GCP_PROJECT,
            bq_dataset=BQ_DATASET,
            table=table_name,
            truncate=True
        )
    print("--- %s seconds ---" % (time.time() - start_time))

def get_all_job_details():

    table_name = 'all_jobs'
    print(f"👀 Fetching list of job ids from BQ!")
    job_refs = download_table_from_bg(table_name)
    print(f"✅List of job ids downloaded from BQ! Total number or jobs = {len(job_refs)}")
    all_details = []
    jwt = get_jwt()
    print(f"✅ Auth token received!")
    start_time = time.time()
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    save_rage = np.arange(1000, 2000000, 1000).tolist()
    num = 0
    for ref in job_refs:
        #print (save_rage)
        print(f"👀 Fetching job ref {ref}. Only {(len(job_refs)-num)} jobs left 🤞🤞🤞")
        job_detail = get_job_detail(jwt, ref)

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
            df.to_csv(f"{LOCAL_DATA_PATH_JOB_DETAILS}/job_details_{timestamp}.csv")
            print(f"✅ Saved {num} jobs to file 'jobs_details_{timestamp}.csv'. Data size =", df.shape)
        num+=1
    print("✅✅✅ DONE for ALL jobs", df.shape)
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    pass
