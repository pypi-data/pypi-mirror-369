# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Test for the expiration of a kerberos principal via LDAP."""

import datetime
import os
import sys

import gssapi
import ldap3
from urllib3.util import parse_url

from ..auth import auth_context
from ..cli import IgwnMonitorArgumentParser
from ..http import make_url
from ..utils import NagiosStatus
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

DEFAULT_LDAP_SERVER = "ldap.ligo.org"
DEFAULT_LDAP_BASE = "ou=keytab,ou=robot,dc=ligo,dc=org"

# servers that we know need GSSAPI (Kerberos) authentication
GSSAPI_LDAP_SERVERS = [
    "ldap.ligo.org",
]


def ldap_connection(
    server,
    auto_bind=True,
    raise_exceptions=False,
    **kwargs,
):
    """Open a connection to an `ldap3.Server`."""
    # default arguments
    connection_kw = {
        "auto_bind": auto_bind,
        "raise_exceptions": raise_exceptions,
    }
    if parse_url(server).host in GSSAPI_LDAP_SERVERS:
        connection_kw.update({
            "authentication": ldap3.SASL,
            "sasl_mechanism": ldap3.GSSAPI,
        })

    # apply user kwargs
    connection_kw.update(kwargs)

    # connect to Server
    server = ldap3.Server(make_url(server, scheme="ldaps").rstrip("/"))
    return ldap3.Connection(server, **connection_kw)


def query_ldap(
    server,
    base,
    filter_,
    **kwargs,
):
    """Query an LDAP server and yield search entries."""
    with ldap_connection(server) as conn:
        conn.search(base, filter_, **kwargs)
        yield from conn.entries


def check_kerberos_principal_expiry(
    principal,
    host=DEFAULT_LDAP_SERVER,
    ldap_base=DEFAULT_LDAP_BASE,
    auth_type="kerberos",
    auth_principal=None,
    auth_keytab=None,
    warning=14,
    critical=7,
):
    ldap_filter = f"(krbPrincipalName={principal})"

    try:
        with auth_context(
            auth_type=auth_type,
            keytab=auth_keytab,
            principal=auth_principal,
        ):
            results = list(query_ldap(
                host,
                ldap_base,
                ldap_filter,
                attributes=["krbPrincipalName", "description"],
            ))
    except gssapi.exceptions.GSSError as exc:
        return (
            NagiosStatus.CRITICAL,
            os.linesep.join((
                f"Error generating TGT for '{auth_principal}'",
                str(exc),
            )),
        )

    if not results:
        return (
            NagiosStatus.CRITICAL,
            f"No LDAP entry found under base '{ldap_base}' "
            f"matching filter '{ldap_filter}'",
        )
    if len(results) > 1:
        return (
            NagiosStatus.CRITICAL,
            f"Incorrect number of entries found ({len(results)})",
        )

    robot = results[0]
    principal = robot["krbPrincipalName"]

    try:
        (year, month, day) = map(int, robot.description.value.split("-"))
    except (
        AttributeError,  # description is None
        TypeError,  # wrong number of date number components
        ValueError,  # description has wrong format
    ):
        return (
            NagiosStatus.UNKNOWN,
            f"Failed to parse '{robot.description.value}' "
            "as YYYY-MM-DD expiry date",
        )

    expiry = datetime.date(year, month, day)
    now = datetime.date.today()
    delta = expiry - now
    warning = datetime.timedelta(days=warning)
    critical = datetime.timedelta(days=critical)

    metric = f"'timeleft'={delta.days}d;{warning.days};{critical.days}"

    if expiry < now:
        return (
            NagiosStatus.CRITICAL,
            f"{principal} expired on {expiry.strftime('%a %d %b %Y')}"
            f" | {metric}",
        )

    message = f"{principal} will expire on {expiry.strftime('%a %d %b %Y')}"
    if delta < critical:
        status = NagiosStatus.CRITICAL
    elif delta < warning:
        status = NagiosStatus.WARNING
    else:
        status = NagiosStatus.OK

    return status, f"{message} | {metric}"


def create_parser():
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
        add_output_options=True,
        add_timeout=True,
    )
    parser.add_argument(
        "-H",
        "--hostname",
        required=True,
        help="URI of LDAP server to query",
    )
    parser.add_argument(
        "-p",
        "--principal",
        required=True,
        type=str,
        help="Kerberos principal whose expiration is being tested",
    )
    parser.add_argument(
        "-b",
        "--ldap-base",
        default=DEFAULT_LDAP_BASE,
        type=str,
        help="LDAP search base",
    )
    parser.add_argument(
        "-w",
        "--warning-threshold",
        default=14,
        type=int,
        help="Number of days remaining that defines WARNING",
    )
    parser.add_argument(
        "-c",
        "--critical-threshold",
        default=7,
        type=int,
        help="Number of days remaining that defines CRITICAL",
    )

    parser.add_auth_argument_group(
        auth_type=("none", "kerberos"),
        kerberos=False,
        principal=True,
        keytab=True,
        scitoken=False,
    )

    return parser


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)
    status, message = check_kerberos_principal_expiry(
        opts.principal,
        host=opts.hostname,
        ldap_base=opts.ldap_base,
        warning=opts.warning_threshold,
        critical=opts.critical_threshold,
        auth_type=opts.auth_type,
        auth_keytab=opts.kerberos_keytab,
        auth_principal=opts.kerberos_principal,
    )
    return write_plugin_output(
        status,
        message,
        file=opts.output_file,
        expiry=opts.output_json_expiry,
        name=PROG,
    )


# module execution
if __name__ == "__main__":
    sys.exit(main())
