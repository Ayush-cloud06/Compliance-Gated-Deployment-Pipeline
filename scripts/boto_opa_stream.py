from boto3_ec2_audit import collect_ec2
from boto3_iam_audit import collect_iam
from boto3_s3_audit import collect_s3
import json, os

opa_input = {
    "environment": "prod",
    "ec2": collect_ec2(),
    "iam": collect_iam(),
    "s3": collect_s3()
}

os.makedirs("reports/opa", exist_ok=True)

with open("reports/opa/input.json", "w") as f:
    json.dump(opa_input, f, indent=2)

print("OPA input generated")
