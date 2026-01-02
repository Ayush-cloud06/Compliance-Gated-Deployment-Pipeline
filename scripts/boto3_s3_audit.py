import boto3

s3 = boto3.client("s3")

buckets = s3.list_buckets()["Buckets"]

s3_data = {
    "total_buckets": len(buckets),
    "public_buckets": []
}

for bucket in buckets:
    name = bucket["Name"]
    try:
        acl = s3.get_bucket_acl(Bucket=name)
        for grant in acl["Grants"]:
            if "AllUsers" in str(grant["Grantee"]):
                s3_data["public_buckets"].append(name)
    except Exception:
        pass

return s3_data
