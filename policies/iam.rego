package compliance.iam

import data.compliance.lib

# METADATA
# title: Console IAM users must have MFA in production
# custom:
#   policy_id: iam_mfa_required
#   severity: high
deny contains decision if {
	lib.is_prod
	some user in input.iam.users_without_mfa

	decision := lib.decision(
		rego.metadata.rule(),
		"iam_user",
		user,
		"IAM user with console access has no MFA in production",
	)
}
