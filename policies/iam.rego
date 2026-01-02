package compliance.iam

deny[result] if {
  input.environment == "prod"
  count(input.iam.users_without_mfa) > 0

  result := {
    "policy": "iam_mfa_required",
    "reason": "IAM users without MFA in production",
    "users": input.iam.users_without_mfa
  }
}

