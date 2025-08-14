# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check availability of a host using nmap."""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

import os
import re
import subprocess
import sys
from shutil import which

from ..cli import IgwnMonitorArgumentParser
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

NMAP = which("nmap") or "/usr/bin/nmap"
NMAP_LATENCY_REGEX = re.compile(
    r"Host is up \((?P<latency>[0-9\.]+)s latency\)",
)


def check_nmap(
    host,
    timeout=60.,
):
    """Ping a Mattermost server and evaluate the reponse status."""
    proc = subprocess.run([
        NMAP,
        "-sn",
        host,
        "--host-timeout", str(timeout),
    ], capture_output=True)

    if proc.returncode:
        return (
            NagiosStatus.CRITICAL,
            os.linesep.join(("nmap failed", str(proc.stderr.decode("utf-8")))),
        )

    stdout = proc.stdout.decode("utf-8").strip()
    stderr = proc.stderr.decode("utf-8").strip()
    lines = stdout.splitlines()

    if stderr.startswith("Failed to resolve"):
        return NagiosStatus.CRITICAL, stderr,

    for pattern, summary in [
        ("Note: Host seems down", "Host seems down"),
        ("0 hosts up", f"Failed to ping {host}"),
    ]:
        if any(pattern in line for line in lines):
            return NagiosStatus.CRITICAL, os.linesep.join((
                summary,
                stdout,
            ))

    try:
        summary = lines[2].rstrip(".")
    except IndexError:
        return NagiosStatus.WARNING, os.linesep.join((
            "Failed to parse nmap output",
            stdout,
        ))

    try:
        latency = float(NMAP_LATENCY_REGEX.search(stdout).groups()[0])
    except (
        AttributeError,  # regex didn't match
        TypeError,  # regex didn't yield a numeric string
    ):
        # don't care, carry on
        pass
    else:
        perfdata = format_performance_metrics({
            "latency": latency,
        }, unit="s")
        summary += f"|{perfdata}"

    return NagiosStatus.OK, summary


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
        required=True,
        help="hostname of Mattermost instance",
    )
    return parser


def main(args=None):
    """Run the thing."""
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_nmap(
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
