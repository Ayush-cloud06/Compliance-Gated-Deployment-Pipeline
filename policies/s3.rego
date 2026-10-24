package compliance.s3

import data.compliance.lib

# METADATA
# title: No public S3 buckets in production
# custom:
#   policy_id: s3_public_bucket_block
#   severity: high
deny contains decision if {
	lib.is_prod
	some bucket in input.s3.public_buckets

	decision := lib.decision(
		rego.metadata.rule(),
		"s3_bucket",
		bucket,
		"Public S3 bucket in production",
	)
}

# METADATA
# title: S3 buckets must be verifiable in production
# description: Fail closed. A bucket the collector could not inspect can't be proven private.
# custom:
#   policy_id: s3_bucket_unverifiable
#   severity: medium
deny contains decision if {
	lib.is_prod
	some bucket in input.s3.unknown_buckets

	decision := lib.decision(
		rego.metadata.rule(),
		"s3_bucket",
		bucket,
		"S3 bucket could not be inspected (access denied or error) in production",
	)
}
