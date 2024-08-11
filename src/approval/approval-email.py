# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import boto3
import os

ses = boto3.client('ses')

def lambda_handler(event, context):
    bucket_name = os.environ['APP_BUCKET']
    shared_inbox_email = os.environ['SHARED_INBOX_MAIL']
    source_email = os.environ['SES_EMAIL']
    email_content = f"Hi Team, \n \n The uploaded code in {bucket_name} has failed the sonar scan. This has been approved as an exception.\n \n Next Steps: \n 1. To continue with deployment, please raise a cloud ticket with this approval email attached.\n\n 2. Please ensure that all security vulnerabilities are addressed prior to any future uploads.\n\nThanks\n Release manager"
    email_subject = f"Approval Received from the Slack channel"
    email_params = {
        'Destination': {
            'ToAddresses': [f'{shared_inbox_email}']
        },
        'Message': {
            'Body': {
                'Text': {'Data': email_content}
            },
            'Subject': {'Data': email_subject}
        },
        'Source': f'{source_email}'
    }

    try:
        response = ses.send_email(**email_params)
        print("Email sent successfully")
        return {
            'statusCode': 200,
            'body': json.dumps('Approval Email sent successfully')
        }
    except Exception as e:
        print("Error sending email:", e)
        return {
            'statusCode': 500,
            'body': json.dumps('Error sending email')
        }
