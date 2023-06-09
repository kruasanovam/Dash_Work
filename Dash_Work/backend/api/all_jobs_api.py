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

@retry
def search_jobs(jwt, arbeitsort=None, umkreis=None, branche=None, page=None, page_size=None):
    """search for jobs. params can be found here: https://jobsuche.api.bund.dev/"""
    URL = 'https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs'

    params = (
        ('arbeitsort', arbeitsort),
        ('umkreis', umkreis),
        ('branche', branche),
        ('page', page),
        ('size', page_size)
    )

    headers = {
        'User-Agent': 'Jobsuche/2.9.2 (de.arbeitsagentur.jobboerse; build:1077; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'OAuthAccessToken': jwt,
        'Connection': 'keep-alive',
    }

    response = requests.get(url=URL, headers=headers, params=params, verify=False)

    if response.status_code != 200:
        if response.status_code in [401, 403]:
            print ("Maybe token is expired? Trying with a new token")
            headers['OAuthAccessToken'] = get_jwt()
            response = requests.get(url=URL, headers=headers, params=params, verify=False)
        else:
            print ("Something is wrong...here is the responce:")
            print (response.status_code)
            print (response.content)

    return response.json()


def get_branches_per_arbeitsort(jwt, arbeitsort, umkreis):
    response = search_jobs(jwt, arbeitsort=arbeitsort, umkreis=umkreis).get("facetten")
    branches = response.get("branche")
    branches_list = []
    if branches is not None:
        branches_list = list(branches.get("counts"))
    return branches_list
