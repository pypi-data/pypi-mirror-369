"""
Set the risk level for a Change by using the pre-defined Risk Assessment Value (RAV) Calculator. 

The RAV is calculated using the following Risk Assessment questions:
Question 
    Weight (Value)  : Possible Answers

Outage Scope/Complexity 
    8   :   Complete service outage or high complexity involving coordinating activity of multiple services, groups, or vendors. Service down during maintenance window.
    4   :   Partial service outage / degradation or moderate complexity involving coordinating activity of multiple services, groups, or vendors. Likely to experience loss of functionality or capacity during maintenance window.
    2   :   Minor service outage / degradation or low complexity involving coordinating activity of single services or groups. Likely to experience short loss of functionality or capacity during maintenance window.
    0   :   No impact or complexity

Locations or # Business
    8   :   Units Impacted Enterprise or > 4 BUs
    2   :   Single location or 1 BU
    1   :   Single location and 0 BUs

Business Impact
    8   :   Very high impact or visibility for ADP businesses. Will impact downstream systems.
    4   :   Medium impact or visibility for affected customers. Likely to affect downstream systems.
    1   :   Low impact or visibility for affected customers. Not likely to affect downstream services.

Backout /Rollback Plan 
    8   :   Unable to back out change or requires a complete system restore if implementation fails. Will or likely to require additional downtime
    4   :   Challenging level of difficulty to backout or backout not desired due to dependencies on data and other systems regardless of level of documentation available. 
            Likely to require additional downtime outside maintenance window to complete backout plan.
    2   :   Moderate level of difficulty to backout due to dependencies on data and other system or inadequate documentation. Likely able to complete backout within the maintenance window.
    1   :   Routine level of difficulty to backout. Adequate documentation and similar backout has been performed in the past. Able to complete backout within the maintenance window.
    0   :   Fully automated rollback within maintenance window.

Experience with Change
    8   :   No experience with this type of change or unable to fully test the change.
    6   :   Limited experience or success in making this type of change or unable to fully test the change. Few previous changes of this type successfully completed.
    2   :   Moderate experience with this type of change or the ability to partially test the change. Most previous changes of this type were successfully completed.
    1   :   Extensive experience with this type of change or ability to fully test the change. Previous changes of this type successfully completed.

Certification 
    8   :   Unable to identify and verify successful operation of all affected application and configuration items.
    0   :   Able to identify and verify successful operation of all affected application and configuration items.
"""
import requests
import logging
import json
import sys

class AssessRisk:
    def __init__(self, url, headers, body):
        self.headers = headers
        self.url = url
        self.body = body

    def retrieve_change(self):
        response = requests.post(self.url, headers=self.headers, data=self.body)
          
        if (response.status_code != 200 and response.status_code != 201):
            logging.error({'Status:': response.status_code})
            logging.error({'Full response:': response.json()})
            sys.exit(1)

        # Decode the JSON response into a dictionary and use the data
        resp = response.json()
        return resp

def risk_assessment(sn_instance, sn_access_token, change_number):
    url = f'https://{sn_instance}.service-now.com/api/audp/adp_change/change_risk_assessment/{change_number}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {sn_access_token}'
        }

    body = {
        "Outage Scope/Complexity": {
            "value": "2"
        },
        "Business Impact": {
            "value": "4"
        },
        "Backout /Rollback Plan": {
            "value": "0"
        },
        "Experience with Change": {
            "value": "1"
        },
        "Locations or # Business Units Impacted": {
            "value": "8"
        },        
        "Certification": {
            "value": "0"
        }
    }
    co = AssessRisk(url, headers, json.dumps(body))
    sn_co = co.retrieve_change()
    return sn_co