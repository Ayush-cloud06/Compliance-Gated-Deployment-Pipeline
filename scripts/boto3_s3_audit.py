import boto3
from botocore.exceptions import ClientError


def collect_s3():
    s3 = boto3.client("s3")
    buckets = s3.list_buckets()["Buckets"]

    s3_data = {"total_buckets": len(buckets), "public_buckets": []}

    for bucket in buckets:
        name = bucket["Name"]
        try:
            acl = s3.get_bucket_acl(Bucket=name)
        except ClientError as e:
            print(f"warning: cannot read ACL for {name}: {e.response['Error']['Code']}")
            continue
        for grant in acl["Grants"]:
            if "AllUsers" in str(grant["Grantee"]):
                s3_data["public_buckets"].append(name)

    return s3_data
