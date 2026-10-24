"""Collect EC2 facts for OPA: one record per non-terminated instance."""

import boto3

LIVE_STATES = ["pending", "running", "stopping", "stopped"]


def collect_ec2(ec2=None):
    ec2 = ec2 or boto3.client("ec2")
    paginator = ec2.get_paginator("describe_instances")
    pages = paginator.paginate(
        Filters=[{"Name": "instance-state-name", "Values": LIVE_STATES}],
    )

    instances = []
    for page in pages:
        for reservation in page["Reservations"]:
            for inst in reservation["Instances"]:
                instances.append(
                    {
                        "instance_id": inst["InstanceId"],
                        "state": inst["State"]["Name"],
                        "public_ip": "PublicIpAddress" in inst,
                    }
                )

    return {
        "total_instances": len(instances),
        "public_instances": sum(1 for i in instances if i["public_ip"]),
        "instances": instances,
    }
