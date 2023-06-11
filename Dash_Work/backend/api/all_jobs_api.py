import requests
import pandas as pd
import numpy as np
import time
from Dash_Work.backend.data.bq_actions import *
from Dash_Work.params import *
from google.cloud import bigquery
import base64
import csv
import random
from retrying import retry
from Dash_Work.backend.api.general_api import *
from Dash_Work.backend.api.job_details_api import *

### Supress SSL certificate warnings when ssl_verify=False
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
        'User-Agent': 'Jobsuche/2.9.2 (de.arbeitsagentur.jobboerse; build:1077; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'OAuthAccessToken': None,
        'Connection': 'keep-alive',
    }

URL = 'https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs'

@retry
def search_jobs(jwt, arbeitsort=None, umkreis=None, branche=None, page=None, page_size=None):
    """search for jobs. params can be found here: https://jobsuche.api.bund.dev/"""

    headers['OAuthAccessToken']=jwt
    params = (
        ('arbeitsort', arbeitsort),
        ('umkreis', umkreis),
        ('branche', branche),
        ('page', page),
        ('size', page_size)
    )
    headers['OAuthAccessToken']=jwt
    response = requests.get(url=URL, headers=headers, params=params, verify=False)
    retoken = False

    if response.status_code != 200:
        if response.status_code in [401, 403]:
            print ("Maybe token is expired? Trying with a new token")
            headers['OAuthAccessToken'] = get_jwt()
            response = requests.get(url=URL, headers=headers, params=params, verify=False)
            retoken = True
        else:
            print ("Something is wrong...here is the response:")
            print (response.status_code)
            print (response.content)

    return [response.json(), retoken]


def get_branches_per_arbeitsort(jwt, arbeitsort, umkreis):
    response = search_jobs(jwt, arbeitsort=arbeitsort, umkreis=umkreis)[0].get("facetten")
    branches = response.get("branche")
    branches_list = []
    if branches is not None:
        branches_list = list(branches.get("counts"))
    return branches_list


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

def get_all_jobs(places):

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    print(f"STARTING at {timestamp}")
    page_size= 100
    umkreis = 0
    all_jobs = []
    jwt = get_jwt()

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
                page_jobs_api_result = search_jobs(jwt, arbeitsort=place, umkreis=umkreis, branche=branche,
                                page=page, page_size=page_size)
                page_jobs = page_jobs_api_result[0].get("stellenangebote", [])
                if page_jobs_api_result[1]:
                    jwt = get_jwt()
                if page_jobs:
                    #print(f"👀 Downloading jobs for place {place} and branche {branche} from page {page}...")
                    place_jobs.extend(page_jobs)
                    page += 1

        if place_jobs:
            all_jobs.extend(place_jobs)

            if num in save_rage:
                place_df = pd.json_normalize(place_jobs)
                print(f"✅ Downloaded all jobs for place {place}. Data size =", place_df.shape)
                df = pd.json_normalize(all_jobs,sep='_')
                file_path = f"{LOCAL_DATA_PATH_ALL_JOBS}/all_jobs_{timestamp}.csv"
                save_df_to_csv(df, file_path)
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

def save_df_to_csv(df, file_path):
    try:
        df.to_csv(file_path)
        print(f"✅ Saved jobs to {file_path}. Data size =", df.shape)
    except UnicodeEncodeError as e:
        print(f"UnicodeEncodeError when saving df to csv file {str(e)}. List of unsaved jobs: {df['refnr']}")
    except:
        print(f"Something else when wrong when saving df to csv file. List of unsaved jobs: {df['refnr']}")
