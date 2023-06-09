import requests
import pandas as pd
import numpy as np
import time
from Dash_Work.backend.data.bq_actions import *
from Dash_Work.backend.api.general_api import *
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

@retry
def get_job_detail(jwt, job_ref):

    URL = 'https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v2/jobdetails'

    headers = {
        'User-Agent': 'Jobsuche/2.9.3 (de.arbeitsagentur.jobboerse; build:1078; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'OAuthAccessToken': jwt,
        'Connection': 'keep-alive',
    }
    response = requests.get(
                url = f'{URL}/{(base64.b64encode(job_ref.encode())).decode("UTF-8")}',
                headers=headers, verify=False)

    if response.status_code != 200:
        if response.status_code in [401, 403]:
            headers['OAuthAccessToken'] = get_jwt()
            response = requests.get(
                    url = f'{URL}/{(base64.b64encode(job_ref.encode())).decode("UTF-8")}',
                    headers=headers, verify=False)
        else:
            print ("Something is wrong...here is the responce:")
            print (response.status_code)
            print (response.content)

    return response.json()
