package tests.iam

import data.compliance.iam

test_one_decision_per_user_without_mfa if {
	result := iam.deny with input as {"environment": "prod", "iam": {"users_without_mfa": ["alice", "bob"]}}
	{d.resource_id | some d in result} == {"alice", "bob"}
	every d in result {
		d.policy == "iam_mfa_required"
		d.resource_type == "iam_user"
	}
}

test_all_users_have_mfa_allowed if {
	count(iam.deny) == 0 with input as {"environment": "prod", "iam": {"users_without_mfa": []}}
}

test_non_prod_allowed if {
	count(iam.deny) == 0 with input as {"environment": "dev", "iam": {"users_without_mfa": ["alice"]}}
}
