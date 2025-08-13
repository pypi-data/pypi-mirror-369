import requests
import base64
import json
import urllib3
import logging
import sys

class OAuth:
    def __init__(self, url, headers, body):
        self.url = url
        self.headers = headers
        self.body = body

    def generate_token(self):
        response = requests.post(self.url, headers=self.headers, data=self.body)
        # Check for HTTP codes other than 200
        if (response.status_code != 200 and response.status_code != 201):
            logging.error({"Status:": response.status_code})
            logging.error({"Full response:": response.text})
            sys.exit(1)

        # Decode the JSON response into a dictionary and use the data
        resp = response.json()
        return resp


def get_token(SN_USER, SN_PASSWORD, SN_INSTANCE):
    #Hide SSL verification warnings from display
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # Set the request parameters URL
    url = f"https://{SN_INSTANCE}.service-now.com/api/audp/azure/token"
    cred = f"{SN_USER}:{SN_PASSWORD}"
    cred_bytes = cred.encode("ascii")
    base64_bytes = base64.b64encode(cred_bytes)
    base64_cred = base64_bytes.decode("ascii")

    # Headers
    headers = {
        "Content-Type": "application/json", 
        "Authorization": f"Basic {base64_cred}"
    }

    # initialize token. Uncommented out this body for initializing the token
    body = {
        "grant_type": "password"
    }

    # refresh token. Uncommented out this body for refreshing the token. replace refresh_token value to new one
    # body = {
    #         'grant_type': 'refresh_token',
    #         'refresh_token': [refresh_token]
    #     }

    oauth = OAuth(url, headers, json.dumps(body))
    token_acquired = oauth.generate_token()
    return token_acquired
