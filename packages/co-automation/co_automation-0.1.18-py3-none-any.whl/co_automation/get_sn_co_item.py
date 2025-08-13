import requests
import logging
import sys

class CMDBCi:
    def __init__(self, url, headers):
        self.headers = headers
        self.url = url

    def retrieve_change(self):
        response = requests.get(self.url, headers=self.headers)
          
        if (response.status_code != 200 and response.status_code != 201):
            logging.error({'Status:': response.status_code})
            logging.error({'Full response:': response.json()})
            sys.exit(1)

        # Decode the JSON response into a dictionary and use the data
        resp = response.json()
        return resp

def get_configuration_item(SN_INSTANCE, sn_access_token,configuration_item):
    url = f'https://{SN_INSTANCE}.service-now.com/api/now/table/cmdb_ci?sysparm_query=name={configuration_item}&sysparm_fields=sys_id'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {sn_access_token}'
        }
    co = CMDBCi(url, headers)
    sn_co = co.retrieve_change()
    return sn_co