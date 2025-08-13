'''
Invoke conflict check by accessing SN endpoint. This will start the conflict engine.
The confirmation message is a directive to wait 5 minutes before checking the status.
'''
import requests
import logging
import sys

class ConflictCO:
    def __init__(self, url, headers):
        self.headers = headers
        self.url = url

    def retrieve_change(self):
        response = requests.post(self.url, headers=self.headers)
          
        if (response.status_code != 200 and response.status_code != 201 and response.status_code != 202):
            logging.error({'Status:': response.status_code})
            logging.error({'Full response:': response.json()})
            sys.exit(1)

        # Decode the JSON response into a dictionary and use the data
        resp = response.json()
        return resp
    
    def status_check(self):
        response = requests.get(self.url, headers=self.headers)
          
        if (response.status_code != 200 and response.status_code != 201 and response.status_code != 202):
            logging.error({'Status:': response.status_code})
            logging.error({'Full response:': response.json()})
            sys.exit(1)

        # Decode the JSON response into a dictionary and use the data
        resp = response.json()
        return resp

def start_conflict_check(SN_INSTANCE, access_token, co_number):
    url = f'https://{SN_INSTANCE}.service-now.com/api/audp/adp_change/change/{co_number}/conflict'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
        }
    co = ConflictCO(url, headers)
    sn_co = co.retrieve_change()
    return sn_co

def conflict_status_check(SN_INSTANCE, access_token, co_number):
    url = f'https://{SN_INSTANCE}.service-now.com/api/audp/adp_change/conflict_status_check/{co_number}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
        }
    co = ConflictCO(url, headers)
    sn_co = co.status_check()
    return sn_co