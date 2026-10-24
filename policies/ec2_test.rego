package tests.ec2

import data.compliance.ec2

inst(id, public, state) := {"instance_id": id, "public_ip": public, "state": state}

test_public_running_instance_denied_in_prod if {
	result := ec2.deny with input as {"environment": "prod", "ec2": {"instances": [inst("i-1", true, "running")]}}
	count(result) == 1
	some d in result
	d.policy == "ec2_public_instance_block"
	d.resource_id == "i-1"
	d.resource_type == "ec2_instance"
	d.severity == "high"
}

test_one_decision_per_instance if {
	instances := [inst("i-1", true, "running"), inst("i-2", true, "running"), inst("i-3", false, "running")]
	count(ec2.deny) == 2 with input as {"environment": "prod", "ec2": {"instances": instances}}
}

test_private_instance_allowed if {
	count(ec2.deny) == 0 with input as {"environment": "prod", "ec2": {"instances": [inst("i-1", false, "running")]}}
}

test_stopped_public_instance_allowed if {
	count(ec2.deny) == 0 with input as {"environment": "prod", "ec2": {"instances": [inst("i-1", true, "stopped")]}}
}

test_non_prod_allowed if {
	count(ec2.deny) == 0 with input as {"environment": "dev", "ec2": {"instances": [inst("i-1", true, "running")]}}
}

test_missing_ec2_section_allowed if {
	count(ec2.deny) == 0 with input as {"environment": "prod"}
}
