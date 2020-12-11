# aws-transfer-custom-idp-ssm-parameter-store-apig
This project provides a custom identity provider backed by [AWS SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html). 
This solution is very similar in design [AWS Secrets Manager](https://s3.amazonaws.com/aws-transfer-resources/custom-idp-templates/aws-transfer-custom-idp-secrets-manager-apig.template.yml) the main difference between the two is where and how the user's identity data is stored (SSM Parameter store vs Secret Manager). The other big different is that the value of the Policy attribute should be an ARN to a custom managed policy instead of an inline policy string. This was done to save space and eliminate the need to move to the Advanced tier for parameter store.   

## Deploying the stack
* Clone the repository
* Open a terminal and configure the bucket name of your target Amazon S3 distribution bucket and region where you'd like to deploy
```
export ACCOUNT_NAME=<Name of the aws account to deploy the solution to>
export SOLUTION_NAME=aws-transfer-custom-idp-ssm-parameter-store-apig
export DIST_OUTPUT_BUCKET=<S3 bucket to deploy the solution>
export VERSION=1.0.0
export AWS_REGION=us-east-2
```
_Note:_ You have to manually create an S3 bucket with the name "$DIST_OUTPUT_BUCKET-$AWS_REGION"; 
* Export aws cli [environment variables](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html) in order to set credentials for the account 
* Next make the deploy script executable and run it
```
cd ./deployment
chmod +x ./deploy.sh  \n
./deploy.sh
```
---


Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://www.apache.org/licenses/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and limitations under the License.
