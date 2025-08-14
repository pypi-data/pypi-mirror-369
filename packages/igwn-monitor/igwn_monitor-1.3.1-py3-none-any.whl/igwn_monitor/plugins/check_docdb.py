# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

import sys

import requests
from bs4 import BeautifulSoup

from ..cli import IgwnMonitorArgumentParser
from ..http import (
    make_url,
    response_performance,
)
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

DOCDB_STATISTICS = "cgi-bin/DocDB/Statistics"


def check_docdb(
    host,
    prefix="",
    endpoint=DOCDB_STATISTICS,
    timeout=10,
    **request_kw,
):
    """Query for the `Statistics` endpoint of a DocDB instance."""
    url = make_url(host, prefix, endpoint)
    try:
        resp = requests.get(url, timeout=timeout, **request_kw)
        resp.raise_for_status()
    except requests.RequestException as exc:  # something went wrong
        return NagiosStatus.CRITICAL, str(exc)

    status = NagiosStatus.OK
    message = "DocDB responded OK"
    metrics = format_performance_metrics(response_performance(resp))

    # if we didn't find a StatisticsTable, something is wrong
    soup = BeautifulSoup(resp.content, "html.parser")
    table = soup.body.find("table", {"id": "StatisticsTable"})
    if table is None:
        status = NagiosStatus.WARNING
        message += ", but no statistics were found"

    return status, f"{message}|{metrics}"


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
        help="hostname of DocDB instance",
    )
    parser.add_auth_argument_group()
    return parser


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_docdb(
        opts.hostname,
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
