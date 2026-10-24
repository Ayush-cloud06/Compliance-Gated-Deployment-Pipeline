"""Collect EC2, IAM and S3 facts into a single OPA input document.

Usage:
    python scripts/boto_opa_stream.py --environment prod [--region ap-south-1] [--output PATH]

Set AWS_ENDPOINT_URL=http://localhost:5000 to run against moto_server.
"""

import argparse
import json
import os
from pathlib import Path

import boto3
from boto3_ec2_audit import collect_ec2
from boto3_iam_audit import collect_iam
from boto3_s3_audit import collect_s3


def build_input(session, environment):
    account_id = session.client("sts").get_caller_identity()["Account"]
    return {
        "environment": environment,
        "account_id": account_id,
        "region": session.region_name,
        "ec2": collect_ec2(session.client("ec2")),
        "iam": collect_iam(session.client("iam")),
        "s3": collect_s3(session.client("s3"), session.client("s3control"), account_id),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--environment", required=True, help="e.g. dev, staging, prod")
    parser.add_argument("--region", default=os.environ.get("AWS_REGION", "ap-south-1"))
    parser.add_argument("--output", type=Path, default=Path("reports/opa/input.json"))
    args = parser.parse_args(argv)

    session = boto3.Session(region_name=args.region)
    opa_input = build_input(session, args.environment)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(opa_input, indent=2) + "\n")
    print(f"OPA input written to {args.output}")


if __name__ == "__main__":
    main()
