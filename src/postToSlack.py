# (C) 2020 IBM Corporation
#
# IBM Cloud Functions / OpenWhisk action to post a message to Slack
#

import json,os,sys
import requests

# Post a message to a specific Slack channel via webhook (url).
# The message is formatted in the blocks notation
def post_to_slack(message,url):
    slack_object = json.dumps({'blocks': message})
    response = requests.post(
        url, data=slack_object,
        headers={'Content-Type': 'application/json'}
    )
    # Return the status code
    return response.status_code

# Compose the Slack message based on the notification
def main(args):
    data=[{
		"type": "section",
		"text": {
			"type": "mrkdwn",
			"text": "The following alert has been released. See https://cloud.ibm.com/security-advisor#/dashboard for details"
		}
	},{
		"type": "divider"
	}]
    # Loop over all issue and create section in Slack message
    for issue in args["decoded"]["security-advisor-alerts"]:
        data.append(
	    {
		"type": "section",
		"text": {
			"type": "mrkdwn",
			"text": "*New issue*\nURL: "+issue["issuer-url"]+
                           "\nAccount: "+issue["payload"]["context"]["account_id"]+
                           "\nService: "+issue["payload"]["context"]["service_name"]+
                           "\nResource: "+issue["payload"]["context"]["resource_name"]
		    }
	    })
    # Now post the message to Slack using a webhook
    webhook_url=args["slack_webhook_url"]
    res=post_to_slack(data,webhook_url)
    return {"result": res}

if __name__ == "__main__":
    main(json.loads(sys.argv[1]))
