package tests.s3

import data.compliance.s3

test_public_bucket_denied if {
	result := s3.deny with input as {"environment": "prod", "s3": {"public_buckets": ["pub"], "unknown_buckets": []}}
	count(result) == 1
	some d in result
	d.policy == "s3_public_bucket_block"
	d.resource_id == "pub"
	d.resource_type == "s3_bucket"
}

test_unknown_bucket_denied_fail_closed if {
	result := s3.deny with input as {"environment": "prod", "s3": {"public_buckets": [], "unknown_buckets": ["mystery"]}}
	count(result) == 1
	some d in result
	d.policy == "s3_bucket_unverifiable"
	d.severity == "medium"
}

test_no_public_buckets_allowed if {
	count(s3.deny) == 0 with input as {"environment": "prod", "s3": {"public_buckets": [], "unknown_buckets": []}}
}

test_older_input_without_unknown_buckets if {
	count(s3.deny) == 1 with input as {"environment": "prod", "s3": {"public_buckets": ["pub"]}}
}

test_non_prod_allowed if {
	count(s3.deny) == 0 with input as {"environment": "dev", "s3": {"public_buckets": ["pub"], "unknown_buckets": ["x"]}}
}
