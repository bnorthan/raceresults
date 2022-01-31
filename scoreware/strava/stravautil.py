import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import yaml

def read_yml_app_data(yaml_file):

    with open(yaml_file, 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    client_id=data_loaded['client_id']
    client_secret=data_loaded['client_secret']

    return client_id, client_secret

def get_authorization_token(client_id, client_secret):
    # payload to get rereshed strava authorization token
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': '90cc6b363aa7fa8d93dcc24dd94fdad1661f5ca5',
        'grant_type': "refresh_token",
        'f': 'json'
    }

    print("Requesting Token...\n")
    
    auth_url = "https://www.strava.com/oauth/token"
    res = requests.post(auth_url, data=payload, verify=False)

    print(res)

    access_token = res.json()['access_token']
    print("Access Token = {}\n".format(access_token))

def get_athlete_token(client_id, client_secret, code):
    payload = {
        'client_id': client_id,
        'client_secret':client_secret,
        'code': code,
        'grant_type': "authorization_code",
        'f': 'json'
    }

    print("Requesting Token...\n")
    
    auth_url = "https://www.strava.com/oauth/token"
    res = requests.post(auth_url, data=payload, verify=False)
    print(res.json())
    access_token = res.json()['access_token']
    print("Access Token = {}\n".format(access_token))
    return access_token

def get_athlete(access_token):
  
    header = {'Authorization': 'Bearer ' + access_token}
    param = {'per_page': 20, 'page': 1}

    _url = "https://www.strava.com/api/v3/athlete/"

    return requests.get(_url, headers=header, params=param).json()

