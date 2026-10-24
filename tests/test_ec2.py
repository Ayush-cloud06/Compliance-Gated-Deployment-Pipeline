from boto3_ec2_audit import collect_ec2


def _ami(ec2):
    return ec2.describe_images(Owners=["amazon"])["Images"][0]["ImageId"]


def _private_subnet(ec2):
    vpc = ec2.create_vpc(CidrBlock="10.0.0.0/16")["Vpc"]["VpcId"]
    return ec2.create_subnet(VpcId=vpc, CidrBlock="10.0.1.0/24")["Subnet"]["SubnetId"]


def test_empty_account(session):
    assert collect_ec2(session.client("ec2")) == {
        "total_instances": 0,
        "public_instances": 0,
        "instances": [],
    }


def test_public_instance_flagged(session):
    ec2 = session.client("ec2")
    # moto's default subnets auto-assign public IPs, like real default VPCs.
    iid = ec2.run_instances(ImageId=_ami(ec2), MinCount=1, MaxCount=1)["Instances"][0]["InstanceId"]

    result = collect_ec2(ec2)

    assert result["public_instances"] == 1
    assert result["instances"] == [{"instance_id": iid, "state": "running", "public_ip": True}]


def test_private_instance_not_flagged(session):
    ec2 = session.client("ec2")
    ec2.run_instances(ImageId=_ami(ec2), MinCount=1, MaxCount=1, SubnetId=_private_subnet(ec2))

    result = collect_ec2(ec2)

    assert result["total_instances"] == 1
    assert result["public_instances"] == 0


def test_terminated_instances_skipped(session):
    ec2 = session.client("ec2")
    iid = ec2.run_instances(ImageId=_ami(ec2), MinCount=1, MaxCount=1)["Instances"][0]["InstanceId"]
    ec2.terminate_instances(InstanceIds=[iid])

    assert collect_ec2(ec2)["total_instances"] == 0


def test_paginates_beyond_one_page(session):
    ec2 = session.client("ec2")
    ami = _ami(ec2)
    # Separate run_instances calls → separate reservations → multiple pages at MaxResults=5.
    for _ in range(7):
        ec2.run_instances(ImageId=ami, MinCount=1, MaxCount=1)

    assert collect_ec2(ec2, page_size=5)["total_instances"] == 7
