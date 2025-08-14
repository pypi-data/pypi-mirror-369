# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check a token issuer, vaguely."""

import sys

import requests

from ..cli import IgwnMonitorArgumentParser
from ..http import make_url
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]


def create_parser():
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
        add_output_options=True,
        add_timeout=True,
    )
    parser.add_argument(
        "-H",
        "--hostname",
        help="host name of SciToken issuer",
    )
    parser.add_argument(
        "-n",
        "--issuer-name",
        help="name of SciToken issuer",
    )
    return parser


def get_keys(host, issuer, timeout=10., **request_kw):
    config_url = make_url(host, issuer, "/.well-known/openid-configuration")

    with requests.Session() as sess:
        # pull down the OpenID configuration
        resp = sess.get(config_url, timeout=timeout, **request_kw)
        resp.raise_for_status()
        conf = resp.json()
        resp.close()

        # then pull down the list of issuer keys
        jwks_uri = conf["jwks_uri"]
        resp = sess.get(jwks_uri, timeout=timeout, **request_kw)
        resp.raise_for_status()
        return resp.json()["keys"]


def check_scitoken_issuer(host, issuer, timeout=10.):
    try:
        issuer_keys = get_keys(host, issuer, timeout=timeout)
    except requests.RequestException as exc:
        return NagiosStatus.CRITICAL, str(exc)

    nkeys = len(issuer_keys)
    metrics = format_performance_metrics({
        "issuer_keys": (nkeys, 0, None, 0, None),
    })
    message = f"Issuer UP, {nkeys} keys available|{metrics}"

    if not nkeys:
        return NagiosStatus.WARNING, message
    return NagiosStatus.OK, message


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_scitoken_issuer(
        opts.hostname,
        opts.issuer_name,
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
if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
