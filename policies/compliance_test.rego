package tests.compliance

import data.compliance

violating := {
	"environment": "prod",
	"ec2": {"instances": [{"instance_id": "i-1", "public_ip": true, "state": "running"}]},
	"iam": {"users_without_mfa": ["alice"]},
	"s3": {"public_buckets": ["pub"], "unknown_buckets": []},
}

test_aggregate_unions_all_domains if {
	result := compliance.deny with input as violating
	{d.policy | some d in result} == {"ec2_public_instance_block", "iam_mfa_required", "s3_public_bucket_block"}
}

test_aggregate_empty_when_clean if {
	clean := {
		"environment": "prod",
		"ec2": {"instances": []},
		"iam": {"users_without_mfa": []},
		"s3": {"public_buckets": [], "unknown_buckets": []},
	}
	count(compliance.deny) == 0 with input as clean
}
