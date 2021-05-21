import requests
import json
import base64
from jproperties import Properties



configs = Properties()
with open('dg-config.properties', 'rb') as config_file:
    configs.load(config_file)

bugzillaURL = configs.get("BUGZILLA_URL").data
Bugs = f'{configs.get("BUG_LIST").data}'
jiraURL = f'{configs["JIRA_URL"].data}'
jiraprojectkey = f'{configs["PROJECT_KEY"].data}'
jiraUser = f'{configs["JIRA_USERNAME"].data}'
jiraToken  = f'{configs["JIRA_TOKEN"].data}'




def buglist(Bugs):
    bugList = []
    if '-' in Bugs:
        bugList = Bugs.split('-')
        return bugList
    elif ',' in Bugs:
        bugList = Bugs.split(',')
        return bugList
    else:
        bugList.append(Bugs)
        return bugList


def get_bug_details(BugID):

    bugrequestjson = '[ { "ids": ['+BugID+'] } ]'
    requestURL = bugzillaURL+'/bugzilla/jsonrpc.cgi?method=Bug.get&params='+bugrequestjson

    response = requests.get(requestURL)
    if response.status_code == 200:
        print("Sucessfully got the detail of the bug "+ BugID)
        #print(json.dumps(response.json(),sort_keys=True, indent=4))
        innerJson = response.json()['result']['bugs']

        bugDetailList = []

        for d in innerJson:
            patch_request = d['cf_patch_request']
            status = d['status']
            customerDetail = d['cf_customer']
            bugSummary = d['summary']
            buildNumber = d['cf_build_number_new']

            if len(patch_request)!= 0: bugDetailList.append(patch_request[0])
            bugDetailList.append(status)
            if len(customerDetail)!= 0: bugDetailList.append(customerDetail[0])
            else: bugDetailList.append("Customer UnKnown")
            bugDetailList.append(bugSummary)
            if buildNumber != '': bugDetailList.append(buildNumber)
            else : bugDetailList.append(" field is not available")

        print(bugDetailList)
        return bugDetailList
    else:
        return "request fails please check the bug id or connect to VPN before accessing the bugzilla"

def create_bug_jira(summary, description, key):

    URL = jiraURL+'/rest/api/2/issue'

    payload = '{"fields":{"project":{"key":"'+key+'"},"summary":"'+summary+'","description":"'+description+'","issuetype":{"name":"Bug"}}}'

    credentials = (jiraUser + ':' + jiraToken).encode('utf-8')
    base64_encoded_credentials = base64.b64encode(credentials).decode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + base64_encoded_credentials
    }

    response = requests.request("POST", URL, headers=headers, data=payload)
    print(response.json())
    return response.json()


# print(get_bug_details('29871'))
# create_bug_jira('This is a test', 'Running from python methord', 'DGRES')

if __name__ == "__main__":

    print(len(buglist(Bugs)))

    list_1 =[]
    list_1 = buglist(Bugs)

    if len(list_1) == 2:
        xRange = range(int(list_1[0]), int(list_1[1]))
        for bugID in xRange:
            list_2 = get_bug_details(str(bugID))
            if list_2[0] == 'YES' and list_2[1] != 'CLOSED':
                create_bug_jira(list_2[2] +" : "+list_2[3].replace('\"', ''), "Build number "+list_2[4]+ " and the status of the bug is "+ list_2[1], jiraprojectkey)
            else:
                print("Ether Bug " + str(bugID) + " is marked as Patch Required NO or the bug is already closed")
    else:
        for bugID in list_1:
            list_2 = get_bug_details(bugID)
            if list_2[0] == 'YES' and list_2[1] != 'CLOSED':
                create_bug_jira(list_2[2] +" : "+list_2[3].replace('\"', ''), "Build number "+list_2[4]+ " and the status of the bug is "+ list_2[1], jiraprojectkey)
            else:
                print("Ether Bug " + bugID + " is marked as Patch Required NO or the bug is already closed")




