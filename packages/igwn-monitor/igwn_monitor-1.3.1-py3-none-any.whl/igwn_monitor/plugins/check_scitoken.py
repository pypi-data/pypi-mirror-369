# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check that to token exists with the required claims remaining lifetime."""

import json
import os
import sys
import time

from scitokens import (
    Enforcer,
    SciToken,
)

from ..cli import IgwnMonitorArgumentParser
from .utils import write_plugin_output

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"
__version__ = "1.0.0"

PROG = __name__.rsplit(".", 1)[-1]


def load_or_discover_token(path=None):
    """Load a token from a file, or discover one."""
    if path:
        with open(path, "r") as fobj:
            return SciToken.deserialize(fobj.read().strip())
    return SciToken.discover()


def validate_token(token, audience=None, scopes=None, timeleft=0):
    """Validate whether a token is valid."""
    # -- defaults

    # if audience wasn't given and the token is valid for 'ANY'
    # just pick something to pass validation
    if audience in [None, "ANY"] and token["aud"] == "ANY":
        audience = "anything"
    # otherwise if we weren't asked for an audience, use what the token has
    elif audience in [None, "ANY"]:
        audience = token["aud"]

    # if scope wasn't given, borrow one from the token to pass validation
    if scopes is None:
        scopes = [token["scope"].split(" ", 1)[0]]

    # -- enforcement

    enforcer = Enforcer(token["iss"], audience=audience)

    # add validator for timeleft
    def _validate_timeleft(value):
        exp = float(value)
        return exp >= enforcer._now + timeleft

    enforcer.add_validator("exp", _validate_timeleft)

    for scope in scopes:
        # parse scope as scheme:path
        try:
            authz, path = scope.split(":", 1)
        except ValueError:
            authz = scope
            path = None

        # test
        valid = enforcer.test(token, authz, path=path)
        if not valid:
            return valid, enforcer

    return True, enforcer


def check_scitoken(
    path=None,
    scopes=None,
    audience=None,
    warning=0,
    critical=0,
):
    try:
        token = load_or_discover_token(path=path)
    except Exception as exc:
        return 2, str(exc)

    valid, enforcer = validate_token(
        token,
        audience=audience,
        scopes=scopes,
        timeleft=critical,
    )

    claims = json.dumps(dict(token.claims()), indent=2)
    remaining = token["exp"] - int(time.time())

    if not valid:
        status = 2
        message = enforcer.last_failure
    else:
        message = f"Discovered valid token with {remaining}s until expiry"
        status = bool(remaining <= warning)
    return status, os.linesep.join((message, "Claims:", claims))


def create_parser():
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
        add_output_options=True,
        add_timeout=False,  # unsupported
    )
    parser.add_argument(
        "--token-file",
        default=None,
        help=(
            "file from which to read token, if not given WLCG Bearer "
            "Token Discovery protocol is used"
        ),
    )
    parser.add_argument(
        "-a",
        "--audience",
        default=None,
        help="required token audience",
    )
    parser.add_argument(
        "-s",
        "--scope",
        action="append",
        default=[],
        help="required scope, can be given multiple times",
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
    status, message = check_scitoken(
        path=opts.token_file,
        audience=opts.audience,
        scopes=opts.scope,
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
if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
