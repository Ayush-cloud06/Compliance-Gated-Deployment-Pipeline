from boto3_iam_audit import collect_iam


def _console_user(iam, name):
    iam.create_user(UserName=name)
    iam.create_login_profile(UserName=name, Password="Corr3ct-Horse-Battery!")


def _enable_mfa(iam, name):
    serial = iam.create_virtual_mfa_device(VirtualMFADeviceName=f"{name}-mfa")["VirtualMFADevice"][
        "SerialNumber"
    ]
    iam.enable_mfa_device(
        UserName=name,
        SerialNumber=serial,
        AuthenticationCode1="123456",
        AuthenticationCode2="654321",
    )


def test_console_user_without_mfa_flagged(session):
    iam = session.client("iam")
    _console_user(iam, "alice")

    assert collect_iam(iam)["users_without_mfa"] == ["alice"]


def test_console_user_with_mfa_not_flagged(session):
    iam = session.client("iam")
    _console_user(iam, "bob")
    _enable_mfa(iam, "bob")

    result = collect_iam(iam)

    assert result["users_without_mfa"] == []
    assert result["users"] == [{"user_name": "bob", "console_access": True, "mfa_enabled": True}]


def test_programmatic_user_not_flagged(session):
    iam = session.client("iam")
    iam.create_user(UserName="ci-bot")

    result = collect_iam(iam)

    assert result["users_without_mfa"] == []
    assert result["users"][0]["console_access"] is False


def test_mixed_users(session):
    iam = session.client("iam")
    _console_user(iam, "alice")
    _console_user(iam, "bob")
    _enable_mfa(iam, "bob")
    iam.create_user(UserName="ci-bot")

    result = collect_iam(iam)

    assert result["total_users"] == 3
    assert result["users_without_mfa"] == ["alice"]
