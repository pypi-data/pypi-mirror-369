
from functools import partial
from unittest import mock

import ldap3
import pytest

from ...plugins.check_kerberos_principal_expiry import (
    ldap_connection,
    main as check_kerberos_principal_expiry,
)

TEST_PRINCIPAL = "testidentity@EXAMPLE.ORG"


def mock_connection(server, entries=None, **kwargs):
    """Mock `ldap3.Connection`.

    See https://ldap3.readthedocs.io/en/latest/mocking.html
    for documentation.
    """
    conn = ldap_connection(
        server,
        client_strategy=ldap3.MOCK_SYNC,
        **kwargs,
    )
    for entry, params in (entries or {}).items():
        conn.strategy.add_entry(entry, params)
    return conn


def mock_connection_factory(entries):
    """Return a mock_connection with specified `entries`."""
    return partial(mock_connection, entries=entries)


@pytest.mark.parametrize(("expiry", "status", "message"), [
    pytest.param(
        "2100-01-01",
        0,
        f"{TEST_PRINCIPAL} will expire on Fri 01 Jan 2100",
        id="ok",
    ),
    pytest.param(
        "2000-01-01",
        2,
        f"{TEST_PRINCIPAL} expired on Sat 01 Jan 2000",
        id="expired",
    ),
    pytest.param(
        "test",
        3,
        "Failed to parse",
        id="badexpiry",
    ),
    pytest.param(
        None,
        2,
        "No LDAP entry found",
        id="notfound",
    ),
])
def test_check_kerberos_principal_expiry(
    capsys,
    expiry,
    status,
    message,
):
    if expiry is None:
        entries = None
    else:
        entries = {
            "cn=test,ou=keytab,ou=robot,dc=ligo,dc=org": {
                "description": expiry,
                "krbPrincipalName": TEST_PRINCIPAL,
            },
        }

    # mock the LDAP result and run the plugin
    with mock.patch(
        "igwn_monitor.plugins.check_kerberos_principal_expiry.ldap_connection",
        mock_connection_factory(entries),
    ):
        ret = check_kerberos_principal_expiry([
            "--hostname=ldap.example.com",
            f"--principal={TEST_PRINCIPAL}",
            "--auth-type=none",
        ])

    # check the output
    assert ret == status
    stdout = capsys.readouterr().out
    assert stdout.startswith(message)
