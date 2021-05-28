# (C) 2020 IBM Corporation
#
# IBM Cloud Functions / OpenWhisk action to send email via Mailjet

import json
import os
import sys
import requests

# Send an email using Mailjet
def sendEmail(message, mj_key, mj_secret):
    url = "https://api.mailjet.com/v3.1/send"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, auth=(
        mj_key, mj_secret), json=message)
    # Return the status code
    return response.status_code

# Compose the email based on the notification
def main(args):
    # get the email configuration
    mj_config = json.loads(args["mj_config"])
    email = {
        "Messages": [{
            "From": mj_config["FROM"],
            "To": mj_config["TO"],
            "Subject": "New IBM Cloud security alert",
            "TextPart": ""
        }]
    }
    # Loop over all issue and create text body for email
    emailbody = ''
    for issue in args["decoded"]["security-advisor-alerts"]:
        # Not all notifications contain details
        if "issuer-url" in issue:
            emailbody = (emailbody + "New issue:\n==========\nURL: " + issue["issuer-url"] +
                         "\nAccount: " + issue["payload"]["context"]["account_id"] +
                         "\nService: " + issue["payload"]["context"]["service_name"] +
                         "\nResource: " + issue["payload"]["context"]["resource_name"])

    # if the body is empty, indicate so for the email not being rejected due to empty body
    if emailbody == '':
        emailbody="empty body - no alert content"
    # Set TextPart for the email. We are not using HTML
    email["Messages"][0]["TextPart"] = emailbody
    # Now, send the email
    res = sendEmail(email, mj_config["KEY"], mj_config["SECRET"])
    return {"result": res}


if __name__ == "__main__":
    main(json.loads(sys.argv[1]))
