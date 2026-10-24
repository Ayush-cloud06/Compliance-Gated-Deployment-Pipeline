import json

import boto_opa_stream
from moto import mock_aws


def test_build_input_shape(session):
    result = boto_opa_stream.build_input(session, "dev")

    assert result["environment"] == "dev"
    assert result["region"] == "ap-south-1"
    assert set(result) == {"environment", "account_id", "region", "ec2", "iam", "s3"}


def test_cli_writes_input_file(tmp_path):
    out = tmp_path / "opa" / "input.json"
    with mock_aws():
        boto_opa_stream.main(["--environment", "prod", "--output", str(out)])

    data = json.loads(out.read_text())
    assert data["environment"] == "prod"
    assert data["ec2"]["total_instances"] == 0
