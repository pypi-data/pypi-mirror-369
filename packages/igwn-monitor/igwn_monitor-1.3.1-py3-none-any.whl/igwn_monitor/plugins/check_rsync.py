# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check the status of an rsync server."""

import os
import subprocess
import sys
from shutil import which

from ..cli import IgwnMonitorArgumentParser
from ..http import make_url
from ..utils import NagiosStatus
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

RSYNC = which("rsync") or "rsync"
DEFAULT_PORT = 873


def check_rsync(
    host,
    port=DEFAULT_PORT,
    timeout=10.,
):
    if port:
        host += f":{port}"
    target = make_url(host, scheme="rsync")

    proc = subprocess.run(
        [RSYNC, target, "--timeout", str(timeout)],
        check=False,
        capture_output=True,
    )
    if proc.returncode:
        status = NagiosStatus.CRITICAL
        message = "Rsync query failed"
        detail = proc.stderr.decode("utf-8").strip()
    else:
        status = NagiosStatus.OK
        message = "Rsync query OK"
        detail = proc.stdout.decode("utf-8").strip()

    return status, os.linesep.join((message, detail))


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
        "--port",
        default=DEFAULT_PORT,
        help="port on host to query",
    )
    return parser


def main(args=None):
    """Run the thing."""
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_rsync(
        opts.hostname,
        port=opts.port,
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
