# (C) 2021 IBM Corporation
#
# IBM Cloud Functions / OpenWhisk action to prep a notification
# for sending email via SMTP

import json
import os
import sys
import requests

# Compose the email based on the notification
def main(args):
    # get the email configuration
    config = json.loads(args["smtp_config"])

    # Loop over all issue and create text body for email
    emailbody = 'Security Alerts\n-------------------\n\n'
    for issue in args["decoded"]["security-advisor-alerts"]:
        # Not all notifications contain details
        if "issuer-url" in issue:
            emailbody = (emailbody + "New issue:\n==========\nURL: " + issue["issuer-url"] +
                         "\nAccount: " + issue["payload"]["context"]["account_id"] +
                         "\nService: " + issue["payload"]["context"]["service_name"] +
                         "\nResource: " + issue["payload"]["context"]["resource_name"])

    # Set TextPart for the email. We are not using HTML
    config['text'] = emailbody
    # Now, send the email by passing the configuration on to the
    # sending action
    return {"config":config}


if __name__ == "__main__":
    main(json.loads(sys.argv[1]))
