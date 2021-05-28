# IBM Cloud Security Advisor Notifications
The IBM Cloud Security Advisor allows for centralized security management. It offers a unified dashboard that alerts security administrators for an IBM Cloud account of issues and helps them in resolving the issues. Within the IBM Cloud Security Advisor you can [configure notification channels](https://cloud.ibm.com/docs/services/security-advisor?topic=security-advisor-notifications). It means that whenever new issues are found (new findings), notifications are sent to qualifying channels. When setting up notification channels, you need to specify a webhook to receive the notification. You also configure for which security providers and for what severity level a notification should be posted to that channel.

In this repository, we provide Python code for IBM Cloud Functions / Apache OpenWhisk actions. They can be used to implement such a mentioned webhook to receive a notification and post a message to a Slack channel or send it as email. The instructions and code are provided for the email service Mailjet, but other services like SendGrid, sendinblue or Postmark all are very similar and easy to implement. Additionally, sample code for sending emails via regular SMTP is included.

![Architecture](/screenshots/SecAdv_Notifications_Architecture.png)

1. IBM Cloud Security Advisor sends a notification to a webhook implemented as IBM Cloud Functions action.
2. The action processes the notification, composes a message and posts it to a Slack channel or sends it as email.


The following blog posts provide an introduction to this code project:
- IBM Cloud blog: [How to Get IBM Cloud Security Advisor Alerts via Slack or Email](https://www.ibm.com/cloud/blog/ibm-cloud-security-advisor-alerts-via-slack-or-email)
- Henrik's blog: [How to: Slack or email notifications for IBM Cloud security issues](https://blog.4loeser.net/2020/03/how-to-slack-or-email-notifications-for.html)


## Set up webhook and notification channel
In order to receive a notification from the security advisor, process it and post a message to Slack, you need to set up a couple components. This includes the Slack app to post messages, actions to receive a notification and post it to Slack as well as the notification channel in IBM Cloud Security Advisor. Follow the steps below.

#### Prepare
1. You need the IBM Cloud CLI with the functions plugin installed. In order to install, follow [Getting started with tutorials](https://cloud.ibm.com/docs/tutorials?topic=solution-tutorials-getting-started).
2. Download or clone this repository and change into the new directory **security-advisor-notifications**.
3. [Download public key](https://cloud.ibm.com/security-advisor#/notifications) for notification channels and save it to a file `public.key` in the directory **security-advisor-notifications**. The public key is needed to verify intactness of notification payloads. The code in action [receiveNotification.py](/src/receiveNotification.py) will work without, but it is recommended to verify objects.   
**Note**: It could be that you first need to create a notification channel to successfully download the public key. In this case revisit this step later on.
4. **To use Slack**:   
   [Create a Slack app](https://api.slack.com/start) and [use an incoming webhook](https://api.slack.com/messaging/webhooks) to send messages to Slack. Thereafter, [deploy the app to a Slack channel](https://api.slack.com/best-practices/blueprints/per-channel-webhooks), copy the displayed webhook. Save it to a file `webhook.uri`. It is needed when deploying the Cloud Functions actions.

   **To send emails via Mailjet**:   
   Sign up for a [Mailjet](https://www.mailjet.com/) account and obtain the API key and secret. Then, in the directory **security-advisor-notifications**, copy over `mailjet.sample.json` into a new file `mailjet.json`. Edit the values for API key and secret and replace the **Email** value for **From** to the verified email address. This is needed to send out emails.

   **To send emails using SMTP**:   
   Use an SMTP server to send the outgoing emails. To configure details, copy over  `smtp_config.sample.json` into a new file `smtp_config.json`. Edit the values for your service.


#### Deploy
1. Make sure you are logged in to IBM Cloud on the command line and have targeted the right environment. You can use the command `ibmcloud target` to verify.
2. If not present, create an IAM namespace **SecurityFindings**:
   ```
   ibmcloud fn namespace create SecurityFindings
   ```
3. Set the newly created namespace as default for the next commands.
   ```
   ibmcloud fn property set --namespace SecurityFindings
   ```

<details>
<summary>**Slack**:</summary>

4. In the same terminal, execute the following command:   
   ```
   SA_PUBLIC_KEY=$(cat public.key) SLACK_WEBHOOK_URL=$(cat webhook.uri) ibmcloud fn deploy -m manifestSlack.yaml
   ```
   It sets two environment variables based on the file content from the prepare phase above. The variables are used to bind action parameters. See the files [manifestSlack.yaml](manifestSlack.yaml) and the related action code for details.
5. Next, you need to obtain the URL for web-enabled action. It serves as webhook for the notification channel. Execute the following:
   ```
   ibmcloud fn action get security_notifications/notificationToSlack --url
   ```
</details>
<details>
<summary>**Mailjet**:</summary>

4. In the same terminal, execute the following command:   

   ```
   SA_PUBLIC_KEY=$(cat public.key) MAILJET_CONFIG=$(cat mailjet.json) ibmcloud fn deploy -m manifestEmailMailjet.yaml
   ```

   It sets two environment variables based on the file content from the prepare phase above. The variables are used to bind action parameters. See the files [manifestEmailMailjet.yaml](manifestEmailMailjet.yaml) and the related action code for details.
5. Next, you need to obtain the URL for web-enabled action. It serves as webhook for the notification channel. Execute the following:
   ```
   ibmcloud fn action get security_notifications/notificationToEmail --url
   ```
</details>
<summary>**Email via SMTP**:</summary>

4. In the same terminal, execute the following command:   

   ```
   SA_PUBLIC_KEY=$(cat public.key) SMTP_CONFIG=$(cat smtp_config.json) ibmcloud fn deploy -m manifestEmailSMTP.yaml
   ```

   It sets two environment variables based on the file content from the prepare phase above. The variables are used to bind action parameters. See the files [manifestEmailSMTP.yaml](manifestEmailSMTP.yaml) and the related action code for details.
5. Next, you need to obtain the URL for web-enabled action. It serves as webhook for the notification channel. Execute the following:
   ```
   ibmcloud fn action get security_notifications/notificationToEmailbySMTP --url
   ```
</details>


#### Create notification channel
After setting up everything to receive a notification and to post it as message to Slack or send it by email, now it is time to create and configure a notification channel in IBM Cloud Security Advisor:
1. In the browser, navigate to [**Notification channels** in the Security Advisor](https://cloud.ibm.com/security-advisor#/notifications).
2. Click **Add notification channel**. Fill in name, description, etc. For webhook, use the URL obtained in step 5 above. Add the ending `.json` to that URL. [It sets the content type to JSON](https://cloud.ibm.com/docs/openwhisk?topic=cloud-functions-actions_web#actions_web_extra), i.e., indicating Cloud Functions that JSON data will be sent.
3. Click on **(Advanced) Select alert source and finding type** to filter events for which to receive notifications. You can pick from built-in and partner providers, the Config Advisor and [custom findings](https://github.com/data-henrik/security-advisor-findings).
4. Once done, click **Save**. This concludes the setup.

Basic channel configuration:   
![Edit notification channel](screenshots/SecurityAdvisor_EditChannel.png)


Advanced options to select source and finding type:   
![Advanced options to select source and finding type](/screenshots/SecurityAdvisor_Filter.png)

#### Test notifications
With all components set up, now you can test notifications.
1. In the browser and the [**Notification channels** page](https://cloud.ibm.com/security-advisor#/notifications), click on the three dot menu in the line showing the created channel. Select **Test connection**. This initiates sending a small test notification to the configured webhook.
2. Either go to the Slack channel in which you deployed the app or to the inbox of the receiver email account. Check for the message.
3. In the browser, navigate to the [IBM Cloud Functions dashboard](https://cloud.ibm.com/functions/dashboard). Select the region and namespace in which you deployed the actions. Check for action activations. Click on the activations to see details such as content or errors.

Further tests could be 
- to configure receiving Config Advisor notifications for the channel and then performing a [Config Advisor scan](https://cloud.ibm.com/security-advisor#/configadvisor).
- to start a [manual run of a custom scan](https://github.com/data-henrik/security-advisor-findings/blob/master/INSTRUCTIONS.md#run-actions-manually) as discussed in our instructions for custom findings.

Sample message in Slack:

![Slack message about new security finding](/screenshots/SlackMessage_SecurityAlert.png)

Sample email:

![Email with security alert](/screenshots/SecAdv_EmailNotification.png)


## Security Advisor custom findings

See the GitHub repo [data-henrik/security-advisor-findings](https://github.com/data-henrik/security-advisor-findings) for details and blog articles on how to integrate your own security scans and related objects (custom findings) into [IBM Cloud Security Advisor](https://cloud.ibm.com/security-advisor).

## License
See the file [LICENSE](/LICENSE) for details.