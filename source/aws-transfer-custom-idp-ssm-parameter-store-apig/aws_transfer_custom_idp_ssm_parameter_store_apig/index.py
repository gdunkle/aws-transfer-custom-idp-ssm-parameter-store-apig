import os
import json
import boto3
import logging
from botocore.exceptions import ClientError
from botocore.config import Config

scope_down_policy_arn = str(os.environ.get('ScopeDownPolicyArn'))
region = str(os.environ.get('ParameterStoreRegion'))
config = Config(
    retries={
        'max_attempts': 3,
        'mode': 'standard'
    }
)
session = boto3.session.Session(region_name=region)
ssm_client = session.client('ssm', config=config)
iam_client = session.client('iam', config=config)


def lambda_handler(event, context):
    resp_data = {}

    if 'username' not in event or 'serverId' not in event:
        print("Incoming username or serverId missing  - Unexpected")
        return resp_data

    # It is recommended to verify server ID against some value, this template does not verify server ID
    input_username = event['username']
    print("Username: {}, ServerId: {}".format(input_username, event['serverId']));

    if 'password' in event:
        input_password = event['password']
    else:
        print("No password, checking for SSH public key")
        input_password = ''

    # Lookup user's secret which can contain the password or SSH public keys
    resp = get_secret(f"/SFTP/{input_username}")

    if resp != None:
        resp_dict = json.loads(resp)
    else:
        print("Parameter Store exception thrown")
        return {}

    if input_password != '':
        if 'Password' in resp_dict:
            resp_password = resp_dict['Password']
        else:
            print("Unable to authenticate user - No field match in Secret for password")
            return {}

        if resp_password != input_password:
            print("Unable to authenticate user - Incoming password does not match stored")
            return {}
    else:
        # SSH Public Key Auth Flow - The incoming password was empty so we are trying ssh auth and need to return the public key data if we have it
        if 'PublicKey' in resp_dict:
            resp_data['PublicKeys'] = [resp_dict['PublicKey']]
        else:
            print("Unable to authenticate user - No public keys found")
            return {}

    # If we've got this far then we've either authenticated the user by password or we're using SSH public key auth and
    # we've begun constructing the data response. Check for each key value pair.
    # These are required so set to empty string if missing
    if 'Role' in resp_dict:
        resp_data['Role'] = resp_dict['Role']
    else:
        print("No field match for role - Set empty string in response")
        resp_data['Role'] = ''

    # These are optional so ignore if not present
    if 'Policy' in resp_dict:
        policy_arn = resp_dict['Policy']
        resp_data['Policy'] = get_policy(policy_arn)
    if 'HomeDirectoryDetails' in resp_dict:
        print("HomeDirectoryDetails found - Applying setting for virtual folders")
        resp_data['HomeDirectoryDetails'] = resp_dict['HomeDirectoryDetails']
        resp_data['HomeDirectoryType'] = "LOGICAL"
    elif 'HomeDirectory' in resp_dict:
        print("HomeDirectory found - Cannot be used with HomeDirectoryDetails")
        resp_data['HomeDirectory'] = resp_dict['HomeDirectory']
    else:
        print("HomeDirectory not found - Defaulting to /")

    print("Completed Response Data: " + json.dumps(resp_data))
    return resp_data


def get_secret(id):
    try:
        get_parameter_resp = ssm_client.get_parameter(Name=id, WithDecryption=True)
        return get_parameter_resp['Parameter']['Value']
    except ClientError as err:
        logging.error('Error Talking to Parameter Store: ' + err.response['Error']['Code'] + ', Message: ' + str(err))
        return None


def get_policy(arn):
    try:
        policy_resp = iam_client.get_policy(PolicyArn=arn)
        policy_version_resp = iam_client.get_policy_version(PolicyArn=arn,
                                                            VersionId=policy_resp["Policy"]["DefaultVersionId"])
        return json.dumps(policy_version_resp["PolicyVersion"]["Document"])
    except ClientError as err:
        logging.error('Error Talking to IAM: ' + err.response['Error']['Code'] + ', Message: ' + str(err))
        return None


def init_logger():
    global log_level
    log_level = str(os.environ.get('LOG_LEVEL')).upper()
    if log_level not in [
        'DEBUG', 'INFO',
        'WARNING', 'ERROR',
        'CRITICAL'
    ]:
        log_level = 'INFO'
    logging.getLogger().setLevel(log_level)


init_logger()
