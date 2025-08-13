import requests
import json
import urllib3
import logging
import sys

class UpdateChangeOrder:
    def __init__(self, SN_INSTANCE, headers, body):
        # Set the request parameters URL
        url = f"https://{SN_INSTANCE}.service-now.com/api/audp/adp_change/update_normal_change_state"
        self.url = url
        self.headers = headers
        self.body = body

    def patch_change(self):
        response = requests.patch(self.url, headers=self.headers, data=self.body)
        # Check for HTTP codes other than 200
        if (response.status_code != 200 and response.status_code != 201):
            logging.error({"Status:": response.status_code})
            logging.error({"Full response:": response.text})
            sys.exit(1)

        # Decode the JSON response into a dictionary and use the data
        resp = response.json()
        return resp

def change_status(SN_INSTANCE, access_token, co_number):
    #Hide SSL verification warnings from display
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
        }

    body = {
        "change_number": co_number,
        "state":"assess",
        "change_exception_type":"Time-Sensitive Change"
    }
    co = UpdateChangeOrder(SN_INSTANCE, headers, json.dumps(body))
    sn_co = co.patch_change()
    return sn_co

def move_status(SN_INSTANCE, access_token, co_number):
    #Hide SSL verification warnings from display
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
        }

    body = {
        "change_number": co_number,
        "state":"assess"
    }
    co = UpdateChangeOrder(SN_INSTANCE, headers, json.dumps(body))
    sn_co = co.patch_change()
    return sn_co

def cancel_change(SN_INSTANCE, access_token, co_number):
    #Hide SSL verification warnings from display
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
        }

    body = {
        "change_number": co_number,
        "state":"cancelled",
        "closed_notes":"No longer required"
    }
    co = UpdateChangeOrder(SN_INSTANCE, headers, json.dumps(body))
    sn_co = co.patch_change()
    return sn_co
