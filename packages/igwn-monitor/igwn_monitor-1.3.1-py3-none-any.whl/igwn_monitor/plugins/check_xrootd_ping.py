# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Ping an XRootD host with a handshake."""


import socket
import struct
import sys
import time

from ..cli import IgwnMonitorArgumentParser
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

DEFAULT_PORT = 1094


def xrootd_ping(host, port=DEFAULT_PORT, timeout=30):
    # http://xrootd.org/doc/prod/XRdv299.htm
    handshake = struct.pack("!iiiii", 0, 0, 0, 4, 2012)
    reply_struct = "!2shiii"
    reply_len = struct.calcsize(reply_struct)

    # connect, send handshake, and get reply
    start = time.time()

    with socket.create_connection((host, port), timeout=timeout) as conn:
        conn.send(handshake)
        reply = conn.recv(reply_len)

    elapsed = round(time.time() - start, 3)

    # Unpack reply
    _, status, _, _, _ = struct.unpack_from(reply_struct, reply)

    return status == 0, elapsed


def check_xrootd_ping(
    host,
    port=DEFAULT_PORT,
    warning=.5,
    critical=1.,
    timeout=30,
):
    """Perform an XRootD handshake with a host."""
    try:
        success, elapsed = xrootd_ping(host, port=port, timeout=timeout)
    except OSError as exc:
        return NagiosStatus.CRITICAL, str(exc)
    except Exception as exc:
        return NagiosStatus.UNKNOWN, str(exc)

    perfdata = format_performance_metrics({
        "latency": (f"{elapsed}s", warning, critical, 0),
    })

    if success:
        return NagiosStatus.OK, f"XRootD OK | {perfdata}"

    return NagiosStatus.CRITICAL, f"XRootD ping failed | {perfdata}"


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
        help="hostname of XRootD server",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=DEFAULT_PORT,
    )
    parser.add_argument(
        "--warning",
        "-w",
        type=int,
        default=1.,
        help="response time above which to return WARNING",
    )
    parser.add_argument(
        "--critical",
        "-c",
        type=int,
        default=2.,
        help="response time above which to return CRITICAL",
    )
    return parser


def main(args=None):
    """Run the thing."""
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_xrootd_ping(
        opts.hostname,
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
