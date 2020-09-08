import requests
import json

def getRecords():
    url = 'https://surfsedev.service-now.com/api/now/table/x_snc_proactive_pr_incident_ppm_results?sysparm_query=business_service%3D73e63ee8f10de100c976bdb9156a15ba&sysparm_display_value=true&sysparm_exclude_reference_link=true&sysparm_fields=number%2Ccontact_type%2Cbusiness_service%2Cshort_description%2Cdescription%2Cassignment_group'
    user = 'shashank.reddy'
    pwd = 'Dev@19216801'
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200:
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        return
    data = response.json()
    return data