"""Collect S3 facts for OPA: which buckets are effectively public.

A bucket is public if its bucket policy is public or its ACL grants
AllUsers/AuthenticatedUsers, unless S3 Block Public Access (account or
bucket level) neutralises that path. Buckets we can't inspect are
reported as unknown rather than silently treated as private.
"""

import boto3
from botocore.exceptions import ClientError

PUBLIC_GRANTEES = {
    "http://acs.amazonaws.com/groups/global/AllUsers",
    "http://acs.amazonaws.com/groups/global/AuthenticatedUsers",
}
BLOCK_FLAGS = ("BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets")
NO_BLOCK = dict.fromkeys(BLOCK_FLAGS, False)


def _error_code(e):
    return e.response["Error"]["Code"]


def _account_block(s3control, account_id):
    try:
        cfg = s3control.get_public_access_block(AccountId=account_id)
    except ClientError as e:
        if _error_code(e) == "NoSuchPublicAccessBlockConfiguration":
            return NO_BLOCK
        raise
    return {**NO_BLOCK, **cfg["PublicAccessBlockConfiguration"]}


def _bucket_block(s3, name):
    try:
        cfg = s3.get_public_access_block(Bucket=name)
    except ClientError as e:
        if _error_code(e) == "NoSuchPublicAccessBlockConfiguration":
            return NO_BLOCK
        raise
    return {**NO_BLOCK, **cfg["PublicAccessBlockConfiguration"]}


def _policy_is_public(s3, name):
    try:
        return s3.get_bucket_policy_status(Bucket=name)["PolicyStatus"]["IsPublic"]
    except ClientError as e:
        if _error_code(e) == "NoSuchBucketPolicy":
            return False
        raise


def _acl_is_public(s3, name):
    grants = s3.get_bucket_acl(Bucket=name)["Grants"]
    return any(g["Grantee"].get("URI") in PUBLIC_GRANTEES for g in grants)


def _inspect_bucket(s3, name, account_block):
    bucket_block = _bucket_block(s3, name)
    block = {f: account_block[f] or bucket_block[f] for f in BLOCK_FLAGS}

    reasons = []
    if not block["RestrictPublicBuckets"] and _policy_is_public(s3, name):
        reasons.append("bucket_policy")
    if not block["IgnorePublicAcls"] and _acl_is_public(s3, name):
        reasons.append("acl")
    return reasons


def collect_s3(s3=None, s3control=None, account_id=None):
    s3 = s3 or boto3.client("s3")
    s3control = s3control or boto3.client("s3control")
    account_id = account_id or boto3.client("sts").get_caller_identity()["Account"]

    account_block = _account_block(s3control, account_id)

    buckets = []
    for page in s3.get_paginator("list_buckets").paginate():
        for bucket in page["Buckets"]:
            name = bucket["Name"]
            try:
                reasons = _inspect_bucket(s3, name, account_block)
                status = "public" if reasons else "private"
            except ClientError as e:
                reasons, status = [f"error:{_error_code(e)}"], "unknown"
            buckets.append({"name": name, "status": status, "reasons": reasons})

    return {
        "total_buckets": len(buckets),
        "account_public_access_block": account_block,
        "public_buckets": [b["name"] for b in buckets if b["status"] == "public"],
        "unknown_buckets": [b["name"] for b in buckets if b["status"] == "unknown"],
        "buckets": buckets,
    }
