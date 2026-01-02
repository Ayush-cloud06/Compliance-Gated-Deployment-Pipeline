package compliance.ec2

deny contains result if {
    input.environment == "prod"

    some i
    inst := input.ec2.instances[i]

    inst.public_ip == true
    inst.state == "running"

    result := {
        "policy": "ec2_public_instance_block",
        "reason": "Public EC2 instance running in production",
        "resource_id": inst.instance_id
    }
}
