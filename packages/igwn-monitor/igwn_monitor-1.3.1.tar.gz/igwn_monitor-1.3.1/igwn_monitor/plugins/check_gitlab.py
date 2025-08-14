# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check the GitLab readiness API and report as a plugin."""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

import json
import os
import sys

import requests

from ..cli import IgwnMonitorArgumentParser
from ..http import make_url
from ..utils import NagiosStatus
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

DEFAULT_API_PATH = "/-/readiness?all=1"


def check_gitlab(host, path=DEFAULT_API_PATH, timeout=60):
    url = make_url(host, path)
    try:
        resp = requests.get(url, timeout=timeout)
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

    try:
        stat = data["status"].upper()
        status = NagiosStatus[stat]
    except KeyError:
        status = NagiosStatus.WARNING
    message = os.linesep.join((
        f"Status: {stat}",
        "Readiness API response:",
        json.dumps(data, indent=2),
    ))
    return status, message


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
        help="FQDN of GitLab host to check",
    )
    parser.add_argument(
        "-p",
        "--api-path",
        default=DEFAULT_API_PATH,
        help="path of API to query",
    )
    return parser


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)
    status, message = check_gitlab(
        opts.hostname,
        opts.api_path,
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
