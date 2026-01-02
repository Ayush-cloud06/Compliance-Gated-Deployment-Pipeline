import boto3
import json
import os

iam = boto3.client("iam")

users = iam.list_users()["Users"]

iam_data = {
    "total_users": len(users),
    "users_without_mfa": []
}

for user in users:
    mfa = iam.list_mfa_devices(UserName=user["UserName"])["MFADevices"]
    if not mfa:
        iam_data["users_without_mfa"].append(user["UserName"])

return iam_data
