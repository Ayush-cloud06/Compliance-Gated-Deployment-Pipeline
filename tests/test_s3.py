import pytest
from boto3_s3_audit import collect_s3
from botocore.exceptions import ClientError
from conftest import REGION, public_read_policy

ALL_BLOCKED = {
    "BlockPublicAcls": True,
    "IgnorePublicAcls": True,
    "BlockPublicPolicy": True,
    "RestrictPublicBuckets": True,
}


@pytest.fixture
def clients(session):
    s3 = session.client("s3")
    account_id = session.client("sts").get_caller_identity()["Account"]
    return s3, session.client("s3control"), account_id


def _bucket(s3, name):
    s3.create_bucket(Bucket=name, CreateBucketConfiguration={"LocationConstraint": REGION})


def _status(result):
    return {b["name"]: (b["status"], b["reasons"]) for b in result["buckets"]}


def test_private_bucket(clients):
    s3, ctl, acct = clients
    _bucket(s3, "private-bkt")

    result = collect_s3(s3, ctl, acct)

    assert result["public_buckets"] == []
    assert _status(result) == {"private-bkt": ("private", [])}


def test_public_policy_flagged(clients):
    s3, ctl, acct = clients
    _bucket(s3, "policy-bkt")
    s3.put_bucket_policy(Bucket="policy-bkt", Policy=public_read_policy("policy-bkt"))

    result = collect_s3(s3, ctl, acct)

    assert result["public_buckets"] == ["policy-bkt"]
    assert _status(result)["policy-bkt"] == ("public", ["bucket_policy"])


def test_public_acl_flagged(clients):
    s3, ctl, acct = clients
    _bucket(s3, "acl-bkt")
    s3.put_bucket_acl(Bucket="acl-bkt", ACL="public-read")

    assert _status(collect_s3(s3, ctl, acct))["acl-bkt"] == ("public", ["acl"])


def test_authenticated_users_acl_flagged(clients):
    s3, ctl, acct = clients
    _bucket(s3, "authread-bkt")
    s3.put_bucket_acl(Bucket="authread-bkt", ACL="authenticated-read")

    assert collect_s3(s3, ctl, acct)["public_buckets"] == ["authread-bkt"]


def test_bucket_block_public_access_neutralises(clients):
    s3, ctl, acct = clients
    _bucket(s3, "blocked-bkt")
    s3.put_bucket_acl(Bucket="blocked-bkt", ACL="public-read")
    s3.put_bucket_policy(Bucket="blocked-bkt", Policy=public_read_policy("blocked-bkt"))
    s3.put_public_access_block(Bucket="blocked-bkt", PublicAccessBlockConfiguration=ALL_BLOCKED)

    assert _status(collect_s3(s3, ctl, acct))["blocked-bkt"] == ("private", [])


def test_account_block_public_access_neutralises(clients):
    s3, ctl, acct = clients
    _bucket(s3, "acct-blocked-bkt")
    s3.put_bucket_acl(Bucket="acct-blocked-bkt", ACL="public-read")
    ctl.put_public_access_block(AccountId=acct, PublicAccessBlockConfiguration=ALL_BLOCKED)

    result = collect_s3(s3, ctl, acct)

    assert result["public_buckets"] == []
    assert result["account_public_access_block"] == ALL_BLOCKED


def test_unreadable_bucket_reported_unknown(clients, monkeypatch):
    s3, ctl, acct = clients
    _bucket(s3, "denied-bkt")

    def access_denied(**_):
        raise ClientError({"Error": {"Code": "AccessDenied", "Message": "nope"}}, "GetBucketAcl")

    monkeypatch.setattr(s3, "get_bucket_acl", access_denied)

    result = collect_s3(s3, ctl, acct)

    assert result["public_buckets"] == []
    assert result["unknown_buckets"] == ["denied-bkt"]
    assert _status(result)["denied-bkt"] == ("unknown", ["error:AccessDenied"])
