import requests
import logging
import sys
from datetime import datetime


class ChangeOrderAutomation:
    def __init__(self, url, headers):
        self.headers = headers
        self.url = url

    def create_change_order(self, CO_ITEM, start_date, end_date, year_week, requested_by, data_center, environment_name,
                            short_description, description, business_case, communication_plan, impact_analysis,
                            backout_plan, test_plan, implementation_plan, isExpediated = False, isTestMode=False):
        body = {
            "requested_for": requested_by,
            "planned_start_date": start_date,
            "planned_end_date": end_date,
            "short_description": short_description,
            "description": description,
            "configuration_item": CO_ITEM,
            "region": "North America",
            "change_manager": "Michael Zaharako",
            "business_case":business_case,
            "communication_plan": communication_plan,
            "impact_analysis": impact_analysis,
            "backout_plan": backout_plan,
            "test_plan":test_plan,
            "implementation_plan": implementation_plan,
            "certification_group": "CAETCRM_Support",
            "pre_implemetation_test_details":"",
            "affected_cis": "",
            "certifier": "",
            "u_certifier_instructions": "",
            "assignment_group": "CAETCRM_Support",
            "assigned_to": "",
            "comments": "",
            "work_notes": "",
            "does_this_change_impact_personal_data_in_scope": "no",
            "does_this_change_impact_on_how_the_personal_data_is_used": "no",
            "does_this_change_impact_the_way_the_personal_data_is_accessed_or_changed": "no"    
        }
        if isExpediated == True:
            body["expedite_justification"] = "preventative"
        if isTestMode == True:
            return body;
        else:
            response = requests.post(self.url, headers=self.headers, data=str(body))
            # Check for HTTP codes other than 200
            if (response.status_code != 200 and response.status_code != 201):
                logging.error({'Status:': response.status_code})
                logging.error({'Full response:': response.json()})
                sys.exit(1)

            # Decode the JSON response into a dictionary and use the data
            resp = response.json()
            return resp


def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%d-%m-%Y %H:%M:%S")
    d2 = datetime.strptime(d2, "%d-%m-%Y %H:%M:%S")
    return abs((d2 - d1).days)

def create_change_order(SN_INSTANCE, sn_access_token, CO_ITEM, start_date, end_date, year_week,
                        requested_by, data_center, environment_name, short_description, description,
                        business_case, communication_plan, impact_analysis, backout_plan, test_plan,
                        implementation_plan, is_test_mode=False):
    isExpediated = (days_between(datetime.today().strftime('%d-%m-%Y %H:%M:%S'), start_date) < 3)
    if  isExpediated:
        url =  f'https://{SN_INSTANCE}.service-now.com/api/audp/adp_change/create_expedited_change'
    else :
        url = f'https://{SN_INSTANCE}.service-now.com/api/audp/adp_change/create_normal_change'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {sn_access_token}'
        }
    co = ChangeOrderAutomation(url, headers)
    sn_co = co.create_change_order(CO_ITEM, start_date, end_date, year_week, requested_by,
                                    data_center, environment_name, short_description, description,
                                    business_case, communication_plan, impact_analysis, backout_plan, test_plan,
                                    implementation_plan, isExpediated, is_test_mode)
    return sn_co