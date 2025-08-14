# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check the latency of the latest segments available from a DQSegDB server."""

import sys

from dqsegdb2 import api as dqsegdb2_api
from requests import (
    HTTPError,
    RequestException,
)

from ..cli import IgwnMonitorArgumentParser
from ..http import (
    get_with_auth,
    make_url,
    response_message,
    response_performance,
)
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
    to_gps,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

NOW = int(to_gps("now"))
DEFAULT_DURATION = 43200


def find_latest(
    host,
    flag,
    start,
    end,
    active=False,
    timeout=10,
    auth_type="scitoken",
    **request_kw,
):
    ifo, name, version = flag.split(":", 2)

    # construct the URL for the API request
    url = make_url(host, dqsegdb2_api.resources_path(
        ifo,
        name,
        version,
        s=start,
        e=end,
        include="active" if active else "known",
    ))

    # make the request (and check the response code)
    resp = get_with_auth(auth_type, url, timeout=timeout, **request_kw)
    resp.raise_for_status()

    # extract the JSON
    data = resp.json()

    # extract request metrics
    metrics = response_performance(resp)
    try:
        qinfo = data["query_information"]
        metrics.update({
            "server_elapsed_query_time":
                f"{qinfo['server_elapsed_query_time']}s",
        })
    except KeyError:  # no query_information
        pass

    # sort segments by stop time
    if active:
        latest = sorted(data["active"], key=lambda x: x[1])
    else:
        latest = sorted(data["known"], key=lambda x: x[1])

    # return the stop time of the most recent segment (and the metrics)
    return latest[-1][1], metrics


def check_dqsegdb_latency(
    host,
    flag,
    timeout=10,
    warning=None,
    critical=None,
    **auth_kw,
):
    end = NOW
    if critical:
        duration = 2 * critical
    else:
        duration = DEFAULT_DURATION
    start = end - duration

    try:
        latest, metrics = find_latest(
            host,
            flag,
            start,
            end,
            timeout=timeout,
            **auth_kw,
        )
    except IndexError:  # no segments
        return NagiosStatus.CRITICAL, f"No segments in the last {duration}s"
    except HTTPError as exc:  # something went wrong
        return NagiosStatus.UNKNOWN, response_message(exc.response)
    except RequestException as exc:  # something else went wrong
        return NagiosStatus.UNKNOWN, str(exc)

    # calculate the latency
    latency = round(float(NOW - latest), 3)
    if latency.is_integer():
        latency = int(latency)

    # include the latency as a performance metric
    metrics["latency"] = (
        f"{latency}s",
        warning or None,
        critical or None,
        0,
        duration,
    )

    # format the summary message and the performance metrics
    summary = (
        f"Latest known segment for {flag} is {latency} seconds old ({latest})"
    )
    perfdata = format_performance_metrics(metrics)
    message = f"{summary} | {perfdata}"

    if critical and latency >= critical:
        return NagiosStatus.CRITICAL, message
    if warning and latency >= warning:
        return NagiosStatus.WARNING, message
    return NagiosStatus.OK, message


def create_parser():
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
        add_timeout=True,
        add_output_options=True,
    )
    parser.add_argument(
        "-H",
        "--hostname",
        help="URL/FQDN of gwdatafind host to query",
    )
    parser.add_argument(
        "-f",
        "--flag",
        metavar="X1:FLAG-NAME:1",
        help="flag for the name",
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

    status, message = check_dqsegdb_latency(
        opts.hostname,
        opts.flag,
        timeout=opts.timeout,
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
