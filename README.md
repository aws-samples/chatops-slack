## chatops-slack

## Summary
In today's fast-paced software development environment, managing Static Application Security Testing (SAST) scan results efficiently is crucial for maintaining code quality and security. However, many organizations face significant challenges:
1. Delayed awareness of critical vulnerabilities due to inefficient notification systems.
2. Slow decision-making processes caused by disconnected approval workflows.
3. Lack of immediate, actionable responses to SAST scan failures.
4. Fragmented communication and collaboration around security findings.
5. Time-consuming and error-prone manual infrastructure setup for security tooling.

These issues often lead to increased security risks, delayed releases, and reduced team productivity. There is a pressing need for a solution that can streamline SAST result management, enhance team collaboration, and automate infrastructure provisioning to address these challenges effectively.

To address these critical challenges, we present a comprehensive solution that leverages the power of AWS Chatbot to streamline the management of Static Application Security Testing (SAST) scan failures reported via SonarQube. This innovative approach integrates custom actions and notifications into a conversational interface, enabling efficient collaboration and decision-making processes within development teams.

Key features of the solution include:
1. Customized Notifications: Real-time alerts and notifications are delivered directly to team chat channels, ensuring prompt awareness and action on SAST scan vulnerabilities or failures.
2. Conversational Approvals: Stakeholders can initiate and complete approval workflows for SAST scan results seamlessly within the chat interface, accelerating decision-making processes.
3. Custom Actions: The solution allows teams to define and execute custom actions based on SAST scan outcomes, such as automatically triggering emails for quality gate failures, enhancing responsiveness to security issues.
4. Centralized Collaboration: All SAST scan-related discussions, decisions, and actions are kept within a unified chat environment, fostering improved collaboration and knowledge-sharing among team members.
5. Infrastructure as Code (IaC): The entire solution is wrapped with AWS CloudFormation templates, enabling faster and more reliable infrastructure provisioning while reducing manual setup errors.

## Architecture
![Architecture Diagram](./assets/Architecture.png)

## Automated Code Quality Assurance Workflow

1. Code Preparation and Upload: 
    - Developer compresses the codebase into a ZIP file.
    - Developer manually uploads zip file to a designated Amazon S3 bucket.
2. Amazon S3 Event Trigger and AWS Step Functions Orchestration:
    - Amazon S3 upload event triggers an AWS Step Functions workflow.
    - Step Functions orchestrates a SAST (Static Application Security Testing) scan using SonarQube.
    - Workflow monitors AWS CodeBuild job status to determine next actions: 
        * If AWS CodeBuild succeeds (Quality Gate pass), the workflow terminates. 
        * If  AWS CodeBuild fails, a Lambda function is invoked for diagnostics.
3. AWS CodeBuild Execution:
    - Aws CodeBuild job executes SonarQube scan on the uploaded codebase.
    - Scan artifacts are stored in a separate Amazon S3 bucket for auditing and analysis.
4. Failure Analysis (AWS Lambda Function):
    - On AWS CodeBuild failure, the CheckBuildStatus AWS Lambda function is triggered.
    - On AWS CodeBuild success, the process is terminated and no further action is needed.
5. Function analyzes failure cause (Quality Gate failure or other issues)  
    - CheckBuildStatus AWS Lambda creates a custom payload with detailed failure information.
    - CheckBuildStatus AWS Lambda publishes the custom payload to an Amazon SNS topic.
6. Notification System:
    - Amazon SNS forwards the payload to AWS Chatbot for Slack integration.
7. Slack Integration:
    - AWS Chatbot posts a notification in the designated Slack channel.
8. Approval Process:
    - Approvers review the failure details in the Slack notification.
    - Approvers can initiate approval using the "Approve" button in Slack.
9. Approval Handler:
    - An Approval AWS Lambda function processes the approval action from Slack.
    - Function generates a custom message for developer notification.
    - Approval AWS Lambda function publishes the custom message to Amazon SES.
10. Developer Notification: 
    - Amazon SES sends an email to the developers with next steps or required actions.

This workflow combines manual code upload with automated quality checks, provides immediate feedback through Slack,

## Pre-requisites
1. AWS Chatbot to be added to slack the required slack workspace as a plugin. Refer [Add apps to slack workspace](https://slack.com/intl/en-in/help/articles/202035138-Add-apps-to-your-Slack-workspace) for further details. Keep a note of the slack Workspace ID shown on the AWS Console after successful registration.

2. An IAM role with permissions to create and manage the following AWS resources: AWS S3 buckets, AWS Step Functions, AWS CodeBuild, AWS Secrets Manager, AWS Lambda functions, Amazon SNS, Amazon SES, and AWS Chatbot.

3. This solution uses a source email that is created and verified in Amazon SES to send out approval emails. Refer to [Creating and verifying email identities](https://docs.aws.amazon.com/ses/latest/dg/creating-identities.html#verify-email-addresses-procedure) for setup instructions.

4. A destination email address for receiving approval notifications. This can generally be a shared inbox or a particular team distribution list. 

5. An operational SonarQube instance accessible from your AWS account. For SonarQube installation instructions, refer to the official documentation [here](https://docs.sonarsource.com/sonarqube/latest/setup-and-upgrade/install-the-server/introduction/).

6. A SonarQube [user token](https://docs.sonarsource.com/sonarqube/latest/user-guide/user-account/generating-and-using-tokens/) with permissions to trigger and create projects via the pipeline.

7. A configured AWS Chatbot client, with the workspace ID readily available for input in the CloudFormation console. Refer [configure a slack client](https://docs.aws.amazon.com/chatbot/latest/adminguide/slack-setup.html#slack-client-setup) for instructions.

## AWS CloudFormation stack overview:
1. The pre-requisite.yml is to be executed first and expects below parameters:

| Key | Description |
| --------------- | --------------- |
| Stack Name | As per choice |
| S3LambaBucket | As per choice, however it has to be globally unique |
| SonarToken | This is the sonar user token that is mentioned in the pre-requisite section |

2. The other stack app-security.yml gets executed next and expects below parameters:

| Key | Description |
| --------------- | --------------- |
| CKMSKeyArn | Enter the key arn noted from the previous steps |
| CKMSKeyId | Enter the key id noted from the previous steps |
| EnvironmentType | Environment name can be selected from the above list |
| S3LambdaBucket | Enter the name of the bucket that contains the approval.zip and notification.zip. |
| SESEmail | Name of the registered email identity in Amazon SES(performed as a part of the pre-requisite). This will be the source email address. |
| SharedInboxMail | Destination email address where the scan notifications are to be sent |
| SlackChannelId | Channel ID of slack channel. Right Click on channel name→ Channel Details on the slack APP find the channel ID at the bottom |
| SlackWorkspaceId | Enter the slack workspace ID created in the pre-requisite section.  You can get it from the AWS console→ AWS Chatbot→ Configured Clients→ Slack→ WorkspaceID |
| SonarFileDirectory | Enter the directory which contains your sonar.project.<env>.properties file. |
| SonarFileName | Enter the name of the sonar.project.<env>properties file |

## Step function overview
If the quality gate on sonar fails, the flow goes to the CheckBuildStatus function which triggers a notification on the slack channel. Below is an example of the step function status post the quality gate fails:
![Step Function](./assets/Stepfunction.png)

## Notification types
Notification type 1: If the uploaded code has failed in the sonar quality gate.
![Notification 1](./assets/ScanFailure.png)

Notification type 2: If the code build has failed because of some other reason and it needs troubleshooting.
![Notification 2](./assets/OtherFailure.png)

## Deployment Instructions

1. Clone repository using below command:
    git clone “git@github.com:aws-samples/chatops-slack.git“
2. Creation of zip file containing AWS Lambda code.The AWS Lambda function code for the Checkbuildstatus and ApprovalEmail functionality is to be zipped into notification.zip and approval.zip respectively. Below commands can be used:
    cd chatops-slack/src
    chmod -R 775 *
    zip -r approval.zip approval
    zip -r notification.zip notification
3. Execution of the first AWS CloudFormation stack file named pre-requisite.yml
    - Execute the pre-requisite.yml AWS CloudFormation stack: AWSConsole→AWSCloudformation→CreateStack→With New resources→ Next
    - Select the boxes “Choose an existing template” and “Upload a template file”. Click choose file and select pre-requisite.yml.
    - The stack expects below parameters listed above in the code section.
    - Select the role which is defined in the pre-requisites section for creating the resources, Click Next → Then click on Submit.
In the resources and outputs section make a note of the S3Lambda, CKMSKeyArn, CKMSKeyId values that will be used in the following steps.
4. Zip file upload to the S3Lambda bucket created above
    - Upload the notification.zip and approval.zip created as a part of the initial steps into the S3Lambda bucket. This will be used by the following AWS CloudFormation stack to provision the lambda function.
5. Execution of the second AWS CloudFormation stack file named app-security.yml
    - Execute the app-security.yml AWS CloudFormation stack: AWSConsole→Cloudformation→CreateStack→With New resources→ Next
    - Select the boxes “Choose an existing template” and “Upload a template file”. Click choose file and select app-security.yml.
    - The stack expects below parameters listed above in the architecture section.
    - Select the role which is defined in the pre-requisites section for creating the resources, Click Next → Then click on Submit.
6. Testing of the notification setup
    - Go to AWSConsole→ Amazon SNS → Go to Topics→ Select the topic that ends with LambdaToAWSSlackChatbot → Send Test message.
    - On successful test message delivery you should see a notification on the slack channel.
7. Approval flow setup
    - Choose the vertical ellipsis button on the bottom of the above notification in your chat channel.
    - In Manage actions, choose Create.
    - Enter a custom action name E.g: APPROVE. This name is a unique identifier for your custom action.
    - Enter a name for your custom action button E.g APPROVE. This name is shown on a button on your notification. This name should be 20 characters or less and can incorporate emojis.
    - For Custom action type, select Lambda action.
    - Choose Next.
    - Select the AWS account and region where this is deployed.
    - Choose Load Lambdas.
    - In Define Lambda Function, select a Lambda function that ends with ApprovalEmailLambda. Then click Next
    - Then on the Display criteria screen click Save
    - On clicking Save you should see an APPROVE button created
8. Approval flow validation
    - Click on the APPROVE button on slack. 
    - The slackbot should send a notification on the message thread with a confirmation string "Approval Email sent successfully“


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.


## Limitations
Custom actions for AWS Chatbot are currently not supported through AWS CloudFormation. The creation of custom action buttons is a manual process in this version of the solution. Automation of custom action deployment via AWS CloudFormation is planned for future releases, enhancing the overall Infrastructure as Code capabilities of this solution.

