# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check the status of a GWOSC server."""

import json
import os
import sys

import requests

from ..cli import IgwnMonitorArgumentParser
from ..http import (
    DEFAULT_REQUEST_TIMEOUT,
    make_url,
    response_performance,
)
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

DEFAULT_API_PATH = "/eventapi/json/"


def check_gwosc_eventapi(
    host,
    path=DEFAULT_API_PATH,
    timeout=DEFAULT_REQUEST_TIMEOUT,
):
    """Ping a GWOSC server and evaluate the reponse status."""
    url = make_url(host, path)

    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return NagiosStatus.CRITICAL, str(exc)

    try:
        data = resp.json()
    except json.JSONDecodeError:
        return NagiosStatus.WARNING, os.linesep.join((
            "Failed to parse JSON from API query",
            resp.text,
        ))

    metrics = response_performance(resp)
    metrics.update({
        "num_releases": len(data),
    })

    if "GWTC-3-confident" in data:
        summary = "GWOSC server seems OK"
        status = NagiosStatus.OK
    else:
        summary = "GWTC-3-confident not in list of releases"
        status = NagiosStatus.WARNING
    message = os.linesep.join((
        f"{summary}|{format_performance_metrics(metrics)}",
        "Datasets:",
        "  " + f"{os.linesep}  ".join(sorted(data)),
    ))

    return status, message


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
    return parser


def main(args=None):
    """Run the thing."""
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_gwosc_eventapi(
        opts.hostname,
        opts.path,
        timeout=opts.timeout,
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
