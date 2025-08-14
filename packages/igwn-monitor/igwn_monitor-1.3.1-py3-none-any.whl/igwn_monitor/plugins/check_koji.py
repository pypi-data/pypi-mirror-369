# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

import os
import sys
from xmlrpc.client import (
    Fault,
    dumps as xmlrpc_dump,
    loads as xmlrpc_load,
)

import requests

from ..cli import IgwnMonitorArgumentParser
from ..http import (
    make_url,
    response_message,
    response_performance,
)
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

DEFAULT_ENDPOINT = "kojihub"


def request_xmlrpc(
    host,
    method,
    endpoint=DEFAULT_ENDPOINT,
    session=requests,
    timeout=30.,
    **kwargs,
):
    url = make_url(host, endpoint)
    data = xmlrpc_dump((), methodname=method)
    if session is None:
        session = requests  # just use the module
    resp = session.post(url, data=data, timeout=timeout, **kwargs)
    resp.raise_for_status()
    return resp, xmlrpc_load(resp.content)[0][0]


def check_koji(
    host,
    endpoint=DEFAULT_ENDPOINT,
    timeout=30.,
):
    try:
        resp, tags = request_xmlrpc(
            host,
            "listTags",
            endpoint=endpoint,
            timeout=timeout,
        )
    except requests.HTTPError as exc:  # something went wrong
        return (
            NagiosStatus.CRITICAL,
            response_message(exc.response)
        )
    except Fault as exc:
        # parsing the XML failed
        return (
            NagiosStatus.CRITICAL,
            str(exc).strip("<>"),
        )
    except requests.RequestException as exc:  # something went wrong
        return (
            NagiosStatus.CRITICAL,
            os.linesep.join((f"Failed to query {host}", str(exc)))
        )

    # format count as performance metrics
    metrics = format_performance_metrics(
        response_performance(resp, critical_time=timeout) | {
            "num_tags": len(tags),
        },
    )

    # format message
    message = f"Koji responded OK | {metrics}"
    if tags:
        status = NagiosStatus.OK
    else:
        status = NagiosStatus.WARNING

    return status, message


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
        help="URL/FQDN of koji host to query",
    )
    return parser


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_koji(
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
