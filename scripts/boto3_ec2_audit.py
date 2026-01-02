
import boto3
import json
import os

REGION = os.environ.get("AWS_REGION", "ap-south-1")

ec2 = boto3.client("ec2", region_name=REGION)

response = ec2.describe_instances()

instances = []

for reservation in response["Reservations"]:
    for inst in reservation["Instances"]:
        instances.append({
            "instance_id": inst["InstanceId"],
            "state": inst["State"]["Name"],
            "public_ip": "PublicIpAddress" in inst
        })

opa_input = {
    "environment": "prod",
    "ec2": {
        "total_instances": len(instances),
        "public_instances": sum(1 for i in instances if i["public_ip"]),
        "instances": instances
    }
}

os.makedirs("reports/opa", exist_ok=True)

with open("reports/opa/input.json", "w") as f:
    json.dump(opa_input, f, indent=2)

print("OPA input generated:", "reports/opa/input.json")
