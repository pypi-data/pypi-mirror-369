# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Query a GWDataFind server for a given URL and report status
in nagios format.
"""

import os
import sys

import requests

from ..cli import IgwnMonitorArgumentParser
from ..http import (
    get_with_auth,
    make_url,
    response_performance,
)
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

API_PREFIX = "/"
API_VERSION_ENDPOINT = "api/version"
LEGACY_LDR_ENDPOINT = "services/data/v1/gwf.json"


def get_api_version(
    host,
    prefix,
    endpoint="api/version",
    timeout=10.,
    auth_type="any",
    **request_kw,
):
    url = make_url(host, prefix, endpoint)
    try:
        resp = get_with_auth(
            auth_type,
            url,
            timeout=timeout,
            **request_kw,
        )
        resp.raise_for_status()
    except requests.HTTPError as exc:
        # if we checked the default endpoint and it didn't work...
        if (
            exc.response.status_code == 404
            and endpoint == API_VERSION_ENDPOINT
        ):
            # 'ping' the legacy LDR path to see if there is a server running
            return get_api_version(
                host,
                prefix,
                endpoint=LEGACY_LDR_ENDPOINT,
                auth_type=auth_type,
                **request_kw,
            )
        raise

    if endpoint == LEGACY_LDR_ENDPOINT:  # LDR DataFind Server
        return resp, {
            "api_versions": ["ldr"],
            "version": "LDR",
        }
    return resp, resp.json()


def check_gwdatafind(
    host,
    prefix=API_PREFIX,
    token=False,
    timeout=10,
    auth_type="any",
    **request_kw,
):
    metrics = {}

    try:
        resp, version = get_api_version(
            host,
            prefix,
            auth_type=auth_type,
            timeout=timeout,
            **request_kw,
        )
    except requests.RequestException as exc:  # something went wrong
        return NagiosStatus.CRITICAL, os.linesep.join((
            f"Failed to query {host}",
            str(exc),
        ))

    summary = "Server responded OK"
    metrics = format_performance_metrics(response_performance(resp))
    message = os.linesep.join((
        f"{summary}|{metrics}",
        f"Server version: {version['version']}",
        f"Supported APIs: {', '.join(version['api_versions'])}",
    ))
    return NagiosStatus.OK, message


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
        action="store",
        default="localhost",
        help="hostname of GWDataFind server",
    )
    parser.add_argument(
        "-A",
        "--api-prefix",
        default=API_PREFIX,
        help="prefix for API on server",
    )
    parser.add_auth_argument_group()
    return parser


def main(args=None):
    """Run the thing."""
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_gwdatafind(
        opts.hostname,
        prefix=opts.api_prefix,
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
