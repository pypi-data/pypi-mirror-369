# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check an NDS2 server by counting the number of channels."""

import os
import sys

import nds2

from ..auth import kerberos_tgt
from ..cli import IgwnMonitorArgumentParser
from ..compat import nullcontext
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

DEFAULT_PORT = nds2.connection.DEFAULT_PORT


def check_nds2(
    host,
    port=DEFAULT_PORT,
    auth_type="none",
    kerberos_principal=None,
    kerberos_keytab=os.getenv("KRB5_KTNAME"),
):
    if auth_type == "kerberos":
        auth_ctx = kerberos_tgt(
            principal=kerberos_principal,
            keytab=kerberos_keytab,
        )
    else:
        auth_ctx = nullcontext()

    with auth_ctx:
        try:
            conn = nds2.connection(host, port)
            metrics = {
                param.lower(): conn.get_parameter(param)
                for param in conn.get_parameters()
            }
            channel_count = conn.count_channels()
            metrics = {
                "channel_count": f"{channel_count};0",
            }
        except RuntimeError as exc:
            return NagiosStatus.CRITICAL, str(exc)

    message = f"NDS serving {channel_count} channels"
    metrics = format_performance_metrics(metrics)

    if channel_count > 0:
        status = NagiosStatus.OK
    else:
        status = NagiosStatus.WARNING
    return status, f"{message}|{metrics}"


def create_parser():
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
        add_output_options=True,
        add_timeout=False,  # unsupported by NDS2 client
    )
    parser.add_argument(
        "-H",
        "--hostname",
        help="FQDN of NDS(2) host to query",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=DEFAULT_PORT,
        type=int,
        help="Port to use when communicating with host",
    )
    parser.add_auth_argument_group()
    return parser


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_nds2(
        opts.hostname,
        port=opts.port,
        auth_type=opts.auth_type,
        kerberos_principal=opts.kerberos_principal,
        kerberos_keytab=opts.kerberos_keytab,
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
