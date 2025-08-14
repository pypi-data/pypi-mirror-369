# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check that a vault token exists and is accepted by the vault."""

import os
import sys
import tempfile

import requests
from dateutil.parser import parse as parse_datestr

from ..cli import IgwnMonitorArgumentParser
from ..compat import UTC
from ..http import make_url
from .utils import write_plugin_output

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"
__version__ = "1.0.0"

PROG = __name__.rsplit(".", 1)[-1]


def default_vault_token_file():
    """Get the default vault token file.

    This function attempts to reproduce the logic used in `htgettoken`
    to construct the default vault token file.
    """
    # get User ID
    try:
        uid = os.geteuid()
    except AttributeError:  # windows
        uid = os.getlogin()

    # get temporary directory,
    # preferring /tmp always because htgettoken does
    if os.path.isdir("/tmp"):  # noqa: S108
        tmpdir = "/tmp"  # noqa: S108
    else:
        tmpdir = tempfile.gettempdir()

    return os.path.join(tmpdir, f"vt_u{uid}")


def check_token(
    path,
    vault,
    scopes=None,
    audience=None,
    warning=0,
    critical=0,
    timeout=30.,
):
    # load the token
    try:
        with open(path, "r") as file:
            token = file.read().strip()
    except Exception as exc:
        return 2, str(exc)

    try:
        resp = requests.get(
            make_url(
                vault,
                "v1/auth/token/lookup-self",
                scheme="https",
                port=8200,
            ),
            headers={
                "X-Vault-Token": token,
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        details = resp.json()
    except requests.HTTPError as exc:
        resp = exc.response
        return 2, f"'{resp.status_code} {resp.reason}' from {resp.request.url}"
    except requests.RequestException as exc:
        return 2, str(exc)

    issue = parse_datestr(details["data"]["issue_time"]).astimezone(UTC)
    expire = parse_datestr(details["data"]["expire_time"]).astimezone(UTC)

    remaining = details["data"]["ttl"]
    message = os.linesep.join((
        f"Vault token is valid ({remaining}s remaining)",
        f"Issue time  : {issue}",
        f"Duration    : {details['data']['creation_ttl']}",
        f"Expire time : {expire}",
        f"Policies    : {', '.join(sorted(details['data']['policies']))}",
    ))

    if remaining <= critical:
        return 2, message
    if remaining <= warning:
        return 1, message
    return 0, message


def create_parser():
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
        add_output_options=True,
        add_timeout=True,
    )
    parser.add_argument(
        "-f",
        "--token-file",
        default=default_vault_token_file(),
        help=(
            "file from which to read token, if not given WLCG Beare "
            "Token Discovery protocol is used"
        ),
    )
    parser.add_argument(
        "-a",
        "--vault-host",
        required=True,
        help="hostname for vault",
    )
    parser.add_argument(
        "-w",
        "--timeleft-warning",
        default=0,
        type=float,
        help="warning threshold (seconds) on token time remaining",
    )
    parser.add_argument(
        "-c",
        "--timeleft-critical",
        default=0,
        type=float,
        help="critical threshold (seconds) on token time remaining",
    )

    return parser


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)
    status, message = check_token(
        path=opts.token_file,
        vault=opts.vault_host,
        timeout=opts.timeout,
        warning=opts.timeleft_warning,
        critical=opts.timeleft_critical,
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
