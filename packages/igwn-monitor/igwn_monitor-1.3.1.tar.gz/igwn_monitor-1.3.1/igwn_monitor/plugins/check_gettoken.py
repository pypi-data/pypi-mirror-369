# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check that we can get a SciToken using htgettoken."""

import os
import sys
from subprocess import SubprocessError
from time import sleep

from ..auth import scitoken as get_scitoken
from ..cli import IgwnMonitorArgumentParser
from ..utils import NagiosStatus
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]


def check_gettoken(
    require_scopes=None,
    timeout=60,
    **token_kw,
):
    try:
        with get_scitoken(
            strict=True,
            timeout=timeout,
            **token_kw,
        ) as token:
            sleep(1)
            claims = dict(token.claims())
    except SubprocessError as exc:  # htgettoken failed
        return (
            NagiosStatus.CRITICAL,
            os.linesep.join(("htgettoken failed", str(exc))),
        )
    except Exception as exc:  # something else failed
        return (
            NagiosStatus.CRITICAL,
            str(exc),
        )

    message = "Bearer token created OK"
    detail = os.linesep.join((
        "",  # leading linesep
        f"Audience: {claims['aud']}",
        f"Issuer: {claims['iss']}",
        f"Scopes: {claims['scope']}",
    ))

    missing = set(require_scopes or []) - set(claims["scope"].split(" "))
    if missing:
        return (
            NagiosStatus.WARNING,
            message + f" but missing '{missing.pop()}'" + detail
        )

    return NagiosStatus.OK, message + detail


def create_parser():
    """Create an argument parser for this script."""
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
    )
    parser.add_argument(
        "-s",
        "--require-scope",
        action="append",
        help="scope to assert returned by token",
    )
    parser.add_auth_argument_group(scitoken=True)
    return parser


def main(args=None):
    """Run the thing."""
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_gettoken(
        require_scopes=opts.require_scope or [],
        timeout=opts.timeout,
        keytab=opts.kerberos_keytab,
        principal=opts.kerberos_principal,
        vaultserver=opts.token_vaultserver,
        vaulttokenfile=opts.token_vaulttokenfile,
        issuer=opts.token_issuer,
        audience=opts.token_audience,
        scope=opts.token_scope,
        role=opts.token_role,
        credkey=opts.token_credkey,
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
