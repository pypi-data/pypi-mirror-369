# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check the latency of the latest file matching a pattern available
from an XRootD server.
"""

import os
import sys
from urllib.parse import urlparse

from ..auth import auth_context
from ..cli import IgwnMonitorArgumentParser
from ..utils import NagiosStatus
from .check_file_latency import check_file_latency
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]


def check_xrootd_latest(
    host,
    pattern,
    port=1094,
    warning=None,
    critical=None,
    auth_type=None,
    **auth_kw,
):
    # query the XRootD server for all files matching the pattern
    # using appropriate authentication
    #   note: only x509_proxy is supported AFAICT
    with auth_context(auth_type, **auth_kw):
        from XRootD.client import glob as xrootd_iglob
        target = f"xroot://{host}:{port}/{pattern}"
        try:
            files = sorted(xrootd_iglob(target, raise_error=True))
        except RuntimeError as exc:
            return (
                NagiosStatus.UNKNOWN,
                os.linesep.join((
                    "XRootD query failed",
                    str(exc),
                )),
            )

    # keep only the path of the file
    # (replacing leading double slash with single)
    latest = f"/{urlparse(files[-1]).path.lstrip('/')}"

    return check_file_latency(
        latest,
        warning=warning,
        critical=critical,
        disable_find=True,
    )


def create_parser():
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
        add_output_options=True,
        add_timeout=False,  # unsupported
    )
    parser.add_argument(
        "-H",
        "--hostname",
        help="URL/FQDN of XRootD host to query",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=1094,
        help="Port on host to query",
    )
    parser.add_argument(
        "-g",
        "--pattern",
        metavar="GLOB",
        required=True,
        help="Glob-style pattern for which to search",
    )
    parser.add_argument(
        "-w",
        "--warning",
        type=float,
        help="latency (seconds) above which to report WARNING",
    )
    parser.add_argument(
        "-c",
        "--critical",
        type=float,
        help="latency (seconds) above which to report CRITICAL",
    )
    parser.add_auth_argument_group()
    return parser


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)
    status, message = check_xrootd_latest(
        opts.hostname,
        opts.pattern,
        port=opts.port,
        warning=opts.warning,
        critical=opts.critical,
        auth_type=opts.auth_type,
        idp=opts.identity_provider,
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
