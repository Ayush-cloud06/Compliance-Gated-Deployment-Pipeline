package compliance.s3

deny[result] if {
  input.environment == "prod"
  count(input.s3.public_buckets) > 0

  result := {
    "policy": "s3_public_bucket_block",
    "reason": "Public S3 buckets detected in production",
    "buckets": input.s3.public_buckets
  }
}

