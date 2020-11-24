##############################################################################
#  Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.   #
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License").           #
#  You may not use this file except in compliance                            #
#  with the License. A copy of the License is located at                     #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  or in the "license" file accompanying this file. This file is             #
#  distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  #
#  KIND, express or implied. See the License for the specific language       #
#  governing permissions  and limitations under the License.                 #
##############################################################################
from moto import (
    mock_ssm,
    mock_iam
)
import json
import os
import boto3

os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["ParameterStoreRegion"] = "us-east-2"


@mock_ssm
@mock_iam
def test_update_params():
    region = os.environ["ParameterStoreRegion"]
    session = boto3.session.Session(region_name=region)
    setup_ssm(session)
    setup_iam(session)
    event = {'username': 'gdunkle', 'password': 'password', 'protocol': 'SFTP', 'serverId': 's-daa2e56d108d45cfa',
             'sourceIp': '127.0.0.1'}
    from aws_transfer_custom_idp_ssm_parameter_store_apig import (
        index
    )
    resp_data = index.lambda_handler(event, {})
    expected_resp = {"Role": "arn:aws:iam::095948426039:role/sftp-awsgalen-com-TransferFamilyScopeDownRole",
                     "Policy": {"Version": "2012-10-17", "Statement": [{"Condition": {
                         "StringLike": {"s3:prefix": ["/${transfer:HomeFolder}/*", "/${transfer:HomeFolder}"]}},
                                                                        "Action": "s3:ListBucket",
                                                                        "Resource": "arn:aws:s3:::${transfer:HomeBucket}",
                                                                        "Effect": "Allow"}, {
                                                                           "Action": ["s3:PutObject", "s3:GetObject",
                                                                                      "s3:DeleteObject",
                                                                                      "s3:GetObjectVersion"],
                                                                           "Resource": "arn:aws:s3:::${transfer:HomeDirectory}/*",
                                                                           "Effect": "Allow"}, {
                                                                           "Action": ["s3:ListAllMyBuckets",
                                                                                      "s3:GetBucketLocation"],
                                                                           "Resource": "*", "Effect": "Allow"}]},
                     "HomeDirectory": "/sftp.awsgalen.com/gdunkle"}
    assert json.dumps(resp_data) == json.dumps(expected_resp)


def setup_iam(session):
    iam_client = session.client(service_name='iam')
    document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Condition": {
                    "StringLike": {
                        "s3:prefix": [
                            "/${transfer:HomeFolder}/*",
                            "/${transfer:HomeFolder}"
                        ]
                    }
                },
                "Action": "s3:ListBucket",
                "Resource": "arn:aws:s3:::${transfer:HomeBucket}",
                "Effect": "Allow"
            },
            {
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject",
                    "s3:GetObjectVersion"
                ],
                "Resource": "arn:aws:s3:::${transfer:HomeDirectory}/*",
                "Effect": "Allow"
            },
            {
                "Action": [
                    "s3:ListAllMyBuckets",
                    "s3:GetBucketLocation"
                ],
                "Resource": "*",
                "Effect": "Allow"
            }
        ]
    }
    resp = iam_client.create_policy(
        PolicyName="DefaultTransferFamilyScopeDownManagedPolicy", PolicyDocument=json.dumps(document)
    )
    iam_client.create_policy_version(
        PolicyArn=resp["Policy"]["Arn"], PolicyDocument=json.dumps(document), SetAsDefault=True
    )


def setup_ssm(session):
    ssm_client = session.client(service_name='ssm')
    secrets = {
        "PublicKey": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD4HUHiPychqgtg67Vtr7aMSqYXI4jIGYxvpCKmBrOQzuSMWSbZ6KqZ9FSptk6KXQBbmuFDYNVxB7wbSHwQ9Gylkft6CVjKNaRMXZTe5AnWiKY8JgDnQzuGyeedp3j7mkk+U3GkCq4mhAvrD50hvN+86NEJx5cuNO/QKXwgvrObuWueniHu+iXjzzZ+zuku5odSKOT4Hwirvd7ve2eyMUswpUGrIPvHVBRSo0yGYsmDYscNSyA5f/F3V3kwdOWb7cK5Lfz2Lb+SBCtec9QCqmUeFDPa+saLWQYI99bScLwotO9+Npln2pXJxh6igvKlWD5LOXtBrUCk/BmTrtQf80H7 awsgalen@3c22fb0ecfe5.ant.amazon.com",
        "HomeDirectory": "/sftp.awsgalen.com/gdunkle",
        "Role": "arn:aws:iam::095948426039:role/sftp-awsgalen-com-TransferFamilyScopeDownRole",
        "Password": "password",
        "Policy": "arn:aws:iam::123456789012:policy/DefaultTransferFamilyScopeDownManagedPolicy"
    }
    ssm_client.put_parameter(Name='/SFTP/gdunkle', Value=json.dumps(secrets), Type="SecureString")
