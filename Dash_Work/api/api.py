from fastapi import FastAPI
import requests
import pandas as pd

### Supress SSL certificate warnings when ssl_verify=False
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

auth_url = 'https://rest.arbeitsagentur.de/oauth/gettoken_cc'
get_url = 'https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs'

def get_jwt():
    """fetch the jwt token object"""
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

    response = requests.post(auth_url, headers=headers, data=data, verify=False)

    return response.json()

def search(jwt, url):
    """search for jobs. params can be found here: https://jobsuche.api.bund.dev/"""
    headers = {
        'User-Agent': 'Jobsuche/2.9.2 (de.arbeitsagentur.jobboerse; build:1077; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'OAuthAccessToken': jwt,
        'Connection': 'keep-alive',
    }
    response = requests.get(url=url, headers=headers, verify=False)
    return response.json()

"""
Currently set to retrieve 200 pages.
Can be increased later once we want to retrieve more data.
"""
def get_all_jobs(jwt, page_size=100):
    all_jobs = []
    page_jobs = True
    page = 1
    ### Change page!=200 to increase/decrease amount of pages and hence data extracted
    num_pages = 200
    while page_jobs and page <= num_pages:
        print(f"👀 Downloading jobs from page {page}...")
        page_url = get_url + f"?page={page}&size={page_size}"
        page_jobs = search(jwt, page_url).get("stellenangebote", [])
        all_jobs.extend(page_jobs)
        page += 1
    return all_jobs

def save_all_jobs():
    jwt = get_jwt()["access_token"]
    all_jobs = get_all_jobs(jwt)
    df = pd.json_normalize(all_jobs)
    df.to_csv("jobs.csv")

    print("✅ Downloaded all jobs and saved to file 'jobs.csv'. Data size =", df.shape)

    ### TODO: upload data to google cloud/big query


if __name__ == "__main__":
    pass
