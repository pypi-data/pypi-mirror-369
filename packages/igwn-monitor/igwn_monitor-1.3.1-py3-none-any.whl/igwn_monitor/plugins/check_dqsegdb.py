# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Query a DQSegDB server for a given URL and report status as a plugin."""

import json
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

BASE_API_PATH = "/dq"


def check_dqsegdb(
    host,
    path="/",
    api=BASE_API_PATH,
    timeout=10,
    auth_type="any",
    **request_kw,
):
    url = make_url(host, path, api)

    try:
        resp = get_with_auth(auth_type, url, timeout=timeout, **request_kw)
        resp.raise_for_status()
    except requests.HTTPError as exc:
        return NagiosStatus.CRITICAL, os.linesep.join((
            response_message(exc.response),
            str(exc),
        ))
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

    status = NagiosStatus.OK
    message = "DQSegDB server responded OK"

    metrics = response_performance(resp)
    try:
        qinfo = data["query_information"]
        metrics.update({
            "num_observatories": (len(data["Ifos"]), None, None, 0),
            "server_elapsed_query_time": (
                f"{qinfo['server_elapsed_query_time']}s",
                0,  # warning count
                None,  # critical count
                0,  # min value
                None,  # max value
            ),
        })
    except KeyError:
        pass
    if not metrics.get("num_observatories", (1,))[0]:
        status = NagiosStatus.WARNING
        message += ", but Ifos list is empty"
    message += "|" + format_performance_metrics(metrics)

    detail = (
        "API response:\n"
        + json.dumps(data, indent=2)
    )

    return status, os.linesep.join((message, detail))


def create_parser():
    """Create an argument parser for this script."""
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
    )
    parser.add_argument(
        "-H",
        "--hostname",
        default="localhost",
        help="hostname of DQSegDB server",
    )
    parser.add_argument(
        "-p",
        "--path",
        default="/",
        help="path on vhost of DQSegDB server",
    )
    parser.add_argument(
        "-A",
        "--api-path",
        default=BASE_API_PATH,
        help="path for API query",
    )
    parser.add_auth_argument_group()
    return parser


def main(args=None):
    """Run the thing."""
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_dqsegdb(
        opts.hostname,
        path=opts.path,
        api=opts.api_path,
        auth_type=opts.auth_type,
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
