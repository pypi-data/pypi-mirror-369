# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check the status of a Mattermost server."""

import os
import sys

import requests
from requests.compat import json

from ..cli import IgwnMonitorArgumentParser
from ..http import make_url
from ..utils import NagiosStatus
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

DEFAULT_PING_PATH = "/api/v4/system/ping"


def check_mattermost(host, path=DEFAULT_PING_PATH, timeout=30.):
    """Ping a Mattermost server and evaluate the reponse status."""
    try:
        resp = requests.get(
            make_url(host, path),
            timeout=timeout,
        )
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

    # parse the JSON to determine the Mattermost service status
    status = data["status"].upper()
    message = os.linesep.join((
        f"Mattermost service {status}",
        "Ping API response:",
        json.dumps(data, indent=2),
    ))

    if status == "UNHEALTHY":
        return NagiosStatus.WARNING, message
    if status == "FAIL":
        return NagiosStatus.CRITICAL, message
    try:
        return NagiosStatus[status], message
    except KeyError:
        return NagiosStatus.UNKNOWN, message


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
        default="api/v4/system/ping",
        help="path on host to query",
    )
    return parser


def main(args=None):
    """Run the thing."""
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_mattermost(
        opts.hostname,
        path=opts.path,
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
