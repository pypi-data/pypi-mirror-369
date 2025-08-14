# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Nagios plugin to check a simple HTTP GET optionally using an Auth system."""

import os
import sys

import requests

from ..cli import IgwnMonitorArgumentParser
from ..http import (
    get_with_auth,
    make_url,
    response_message,
    response_performance,
)
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]


def check_url(
    url,
    auth_type,
    expected_code=None,
    timeout=30.,
    **request_kw,
):
    """Check a response from a URL.

    Returns the Nagios code and the message to display.

    Anything other than a 200 response will result in a 'CRITICAL'
    notification.
    """
    # make the request and handle the response
    try:
        resp = get_with_auth(
            auth_type,
            url,
            timeout=timeout,
            **request_kw,
        )
        resp.raise_for_status()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code
        message = response_message(exc.response)
        metrics = response_performance(exc.response)
        detail = str(exc)
        code = NagiosStatus.CRITICAL
    except requests.RequestException as exc:
        return NagiosStatus.CRITICAL, str(exc), None
    else:
        status_code = resp.status_code
        message = response_message(resp)
        metrics = response_performance(resp)
        detail = os.linesep.join((
            "Raw output:",
            resp.text,
        )).strip()
        if status_code >= 300:
            code = NagiosStatus.WARNING
        else:
            code = NagiosStatus.OK

    # if we got the code that we were expecting, that's OK
    if expected_code and status_code == expected_code:
        code = NagiosStatus.OK
        message += " (as expected)"
    # otherwise this is at least a WARNING
    elif expected_code:
        code = max(code, NagiosStatus.WARNING)
        message += f" (expected {expected_code})"

    return (
        code,
        "|".join((message, format_performance_metrics(metrics))),
        detail,
    )


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
        default="localhost",
        help="FQDN of host to query",
    )
    parser.add_argument(
        "-p",
        "--path",
        default="/",
        help="path to GET",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="include response text in monitor output",
    )
    parser.add_argument(
        "-c",
        "--expected-http-code",
        type=int,
        default=None,
        help="expected HTTP code number",
    )

    reqargs = parser.add_argument_group("Request arguments")
    reqargs.add_argument(
        "-r",
        "--disable-redirects",
        action="store_true",
        default=False,
        help="disable following redirects from responses",
    )

    parser.add_auth_argument_group()

    return parser


def main(args=None):
    """Run the check."""
    # parse command line arguments
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message, detail = check_url(
        make_url(opts.hostname, opts.path),
        opts.auth_type,
        expected_code=opts.expected_http_code,
        allow_redirects=not opts.disable_redirects,
        timeout=opts.timeout,
        idp=opts.identity_provider,
        kerberos=opts.kerberos,
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

    # if verbose or returned a 3XX code, print the detail:
    if detail and (opts.verbose or status == NagiosStatus.WARNING):
        message = os.linesep.join((message, detail))

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
