import json

import boto3
import pytest
from moto import mock_aws

REGION = "ap-south-1"


@pytest.fixture(autouse=True)
def _fake_aws_env(monkeypatch):
    # Never let a test reach real AWS, even if the dev has credentials or an endpoint set.
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", REGION)
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    monkeypatch.delenv("AWS_ENDPOINT_URL", raising=False)


@pytest.fixture
def session():
    with mock_aws():
        yield boto3.Session(region_name=REGION)


def public_read_policy(bucket):
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket}/*",
                }
            ],
        }
    )
