# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check that we can copy a file from an XRootD server using xrdcp."""

import os
import re
import subprocess
import sys
import time
from shutil import which

from igwn_auth_utils import scitoken_authorization_header
from scitokens import SciToken

from ..auth import auth_context
from ..cli import IgwnMonitorArgumentParser
from ..http import make_url
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

XRDCP = which("xrdcp") or "xrdcp"
DEFAULT_PORT = 1094


def token_header(token):
    return scitoken_authorization_header(token).replace(" ", "%20")


def download_size(content):
    """Return a human-readable statement of the size of the content.

    Parameters
    ----------
    content : bytes
        The encoded content to measure.

    Returns
    -------
    size : `str`
        The size of the content in a human-readable format.

    Examples
    --------
    >>> download_size(b"12345")
    "5 Bytes"
    >>> download_size(b"1" * 1_000_000)
    "1.0 MB"
    """
    size = len(content)
    try:
        from humanize import naturalsize
    except ImportError:
        return f"{size} Bytes"
    return naturalsize(size)


def check_xrdcp(
    host,
    path,
    port=DEFAULT_PORT,
    timeout=30,
    regex=None,
    auth_type=None,
    **auth_kw,
):
    """Check that we can download a file using `xrdcp`."""
    if port:
        host += f":{port}"
    source = make_url(host, scheme="xroot") + "/" + path

    auth_kw.setdefault("token_scope", f"read:{path.rsplit('/', 1)[0]}")

    with auth_context(auth_type, **auth_kw) as auth:
        if isinstance(auth, SciToken):
            source += f"?authz={token_header(auth)}"
        start = time.time()
        proc = subprocess.run(
            [
                XRDCP,
                source,
                "-",
                "--silent",
            ],
            check=False,
            capture_output=True,
            timeout=timeout,
        )
    elapsed = round(time.time() - start, 3)
    if proc.returncode:
        return NagiosStatus.CRITICAL, os.linesep.join((
            "XRootD copy failed",
            proc.stderr.decode("utf-8").strip(),
        ))

    content = proc.stdout
    size = download_size(content)
    message = f"XRootD copy succeeded ({size} rec. in {elapsed}s)"
    perfdata = format_performance_metrics({"elapsed": f"{elapsed}s"})

    if (
        regex is not None
        and not re.search(regex, content.decode("utf-8"))
    ):
        return (
            NagiosStatus.CRITICAL,
            f"{message}, but pattern not found|{perfdata}",
        )

    return NagiosStatus.OK, f"{message}|{perfdata}"


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
        help="hostname of XRootD host",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=DEFAULT_PORT,
        help="port on host to query",
    )
    parser.add_argument(
        "-s",
        "--path",
        required=True,
        help="path to retrieve from host",
    )
    parser.add_argument(
        "-r",
        "--regex",
        help="regex against which to match content of download",
    )
    parser.add_auth_argument_group(
        title="Authorisation arguments (none or scitokens)",
    )
    return parser


def main(args=None):
    """Run the thing."""
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_xrdcp(
        opts.hostname,
        opts.path,
        port=opts.port,
        regex=opts.regex,
        timeout=opts.timeout,
        auth_type=opts.auth_type,
        kerberos_principal=opts.kerberos_principal,
        kerberos_keytab=opts.kerberos_keytab,
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
