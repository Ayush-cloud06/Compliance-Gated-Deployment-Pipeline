"""Collect IAM facts for OPA: console users without MFA (CIS AWS 1.10)."""

import boto3
from botocore.exceptions import ClientError


def _has_console_access(iam, user_name):
    try:
        iam.get_login_profile(UserName=user_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            return False
        raise
    return True


def collect_iam(iam=None):
    iam = iam or boto3.client("iam")

    users = []
    for page in iam.get_paginator("list_users").paginate():
        for user in page["Users"]:
            name = user["UserName"]
            mfa_pages = iam.get_paginator("list_mfa_devices").paginate(UserName=name)
            users.append(
                {
                    "user_name": name,
                    "console_access": _has_console_access(iam, name),
                    "mfa_enabled": any(p["MFADevices"] for p in mfa_pages),
                }
            )

    return {
        "total_users": len(users),
        # Only console users need MFA; access-key-only users can't use it to sign in.
        "users_without_mfa": [
            u["user_name"] for u in users if u["console_access"] and not u["mfa_enabled"]
        ],
        "users": users,
    }
