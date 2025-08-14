# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check the status of a GraCEDB server."""

import json
import os
import sys

import requests

from ..cli import IgwnMonitorArgumentParser
from ..http import (
    get_with_auth,
    make_url,
)
from ..utils import NagiosStatus
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

DEFAULT_API_PATH = "/api/events/?count=1"


def check_gracedb_events(
    host,
    path=DEFAULT_API_PATH,
    auth_type="x509",
    timeout=30.,
    **request_kw,
):
    """Query a GraceDB server for the latest event
    and evaluate the reponse status.
    """
    url = make_url(host, path)

    try:
        resp = get_with_auth(auth_type, url, timeout=timeout, **request_kw)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return NagiosStatus.CRITICAL, str(exc)

    try:
        data = resp.json()
    except json.JSONDecodeError:
        return (
            NagiosStatus.WARNING,
            os.linesep.join((
                "Failed to parse JSON from API query",
                resp.text,
            )),
        )

    detail = os.linesep.join((
        "Events API response:",
        "<pre>",
        json.dumps(data, indent=2).strip(),
        "</pre>",
    ))

    try:
        event = data["events"][0]
    except (KeyError, IndexError):
        state = NagiosStatus.UNKNOWN
        message = "Probable good response, but lacking expected data"
    else:
        state = NagiosStatus.OK
        message = (
            f"Last event '{event['graceid']}' created at '{event['created']}'"
        )

    return state, os.linesep.join((message, detail))


def create_parser():
    """Create an argument parser for this script."""
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
        add_output_options=True,
        add_timeout=True,
    )
    parser.add_argument(
        "-H",
        "--hostname",
        default="localhost",
        help="hostname of Mattermost instance",
    )
    parser.add_argument(
        "-p",
        "--path",
        default=DEFAULT_API_PATH,
        help="path on host to query",
    )
    parser.add_auth_argument_group()
    return parser


def main(args=None):
    """Run the thing."""
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_gracedb_events(
        opts.hostname,
        path=opts.path,
        timeout=opts.timeout,
        auth_type=opts.auth_type,
        idp=opts.identity_provider,
        kerberos_keytab=opts.kerberos_keytab,
        kerberos_principal=opts.kerberos_principal,
        token_vaultserver=opts.token_vaultserver,
        token_issuer=opts.token_issuer,
        token_vaulttokenfile=opts.token_vaulttokenfile,
        token_audience=opts.token_audience,
        token_scope=opts.token_scope,
        token_role=opts.token_role,
        token_credkey=opts.token_credkey,
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
