package compliance.ec2

import data.compliance.lib

# METADATA
# title: No public EC2 instances in production
# custom:
#   policy_id: ec2_public_instance_block
#   severity: high
deny contains decision if {
	lib.is_prod
	some inst in input.ec2.instances
	inst.public_ip == true
	inst.state == "running"

	decision := lib.decision(
		rego.metadata.rule(),
		"ec2_instance",
		inst.instance_id,
		"Public EC2 instance running in production",
	)
}
