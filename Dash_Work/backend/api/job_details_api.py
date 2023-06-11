import requests
import pandas as pd
import numpy as np
import time
from Dash_Work.backend.data.bq_actions import *
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

URL = 'https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v2/jobdetails'

headers = {
        'User-Agent': 'Jobsuche/2.9.3 (de.arbeitsagentur.jobboerse; build:1078; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'OAuthAccessToken': None,
        'Connection': 'keep-alive',
    }

@retry
def get_job_detail(jwt, job_ref):
    headers['OAuthAccessToken']=jwt
    response = requests.get(
                url = f'{URL}/{(base64.b64encode(job_ref.encode())).decode("UTF-8")}',
                headers=headers, verify=False)

    retoken = False

    if response.status_code != 200:
        if response.status_code in [401, 403]:
            print(f"Tried to get job details but got {response.status_code}")
            headers['OAuthAccessToken'] = get_jwt()
            response = requests.get(
                    url = f'{URL}/{(base64.b64encode(job_ref.encode())).decode("UTF-8")}',
                    headers=headers, verify=False)
            retoken = True
        else:
            print ("Something is wrong...here is the response:")
            print (response.status_code)
            print (response.content)

    return [response.json(), retoken]

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
