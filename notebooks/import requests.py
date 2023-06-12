import requests
import pandas as pd
import json


url_token="https://rest.arbeitsagentur.de/oauth/gettoken_cc"
#response=requests.post(url)

#request token
response_token = requests.post(url_token, data={"client_id":'c003a37f-024f-462a-b36d-b001be4cd24a',"client_secret":'32a39620-32b3-4307-9aa1-511e3d7f48a8', "grant_type": "client_credentials"})

token=response_token.json()['access_token']

print(token)

#use token
url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs/"
header={"OAuthAccessToken": token}
#parameter dict for selection for lines
#select which columns to choose in dataframe
#select API for detailed job information
#put detailed jobs in dataframe

params={"wo":"Erfurt"}
response = requests.get(url, headers=header, params=params).json()
print(response)
