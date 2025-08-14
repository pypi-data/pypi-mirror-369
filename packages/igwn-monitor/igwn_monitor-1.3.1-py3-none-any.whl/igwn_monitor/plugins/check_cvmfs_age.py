# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check the timestamp of a CVMFS repository from the Stratum-0."""

import sys
import time

import requests

from ..cli import IgwnMonitorArgumentParser
from ..http import make_url
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

NOW = time.time()


def check_cvmfs_age(
    host,
    repo,
    port=8000,
    timeout=10,
    warning=None,
    critical=None,
):
    url = make_url(
        host,
        f"cvmfs/{repo}/.cvmfspublished",
        scheme="http",
        port=port,
    )
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return NagiosStatus.UNKNOWN, str(exc)

    manifest = resp.text
    epoch = None
    reponame = None
    for line in manifest.splitlines():
        if line.startswith("--"):
            break
        idx = line[0]
        if idx == "T":
            epoch = float(line[1:])
        if idx == "N":
            reponame = str(line[1:])
    if epoch is None or reponame is None:
        return (
            NagiosStatus.UNKNOWN,
            "Failed to parse .cvmfspublished",
        )
    if repo != reponame:
        return (
            NagiosStatus.UNKNOWN,
            f"Repository name '{repo}' doesn't match "
            f".cvmfspublished manifest ('{reponame}')",
        )

    age = int(NOW - epoch)

    summary = f"/cvmfs/{repo} was last published {age}s ago"
    perfdata = format_performance_metrics({
        "age": (f"{age}s", warning or None, critical or None, 0),
    })
    message = f"{summary} | {perfdata}"

    if critical and age >= critical:
        return NagiosStatus.CRITICAL, message
    if warning and age >= warning:
        return NagiosStatus.WARNING, message
    return NagiosStatus.OK, message


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
        help="hostname of Mattermost instance",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=8000,
        type=int,
        help="port to use",
    )
    parser.add_argument(
        "-r",
        "--repository",
        help="the FQRN of the CVMFS repository",
    )
    parser.add_argument(
        "-w",
        "--warning",
        type=float,
        help="age (seconds) above which to report WARNING",
    )
    parser.add_argument(
        "-c",
        "--critical",
        type=float,
        help="age (seconds) above which to report CRITICAL",
    )
    return parser


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)
    status, message = check_cvmfs_age(
        opts.hostname,
        opts.repository,
        port=opts.port,
        timeout=opts.timeout,
        warning=opts.warning,
        critical=opts.critical,
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
