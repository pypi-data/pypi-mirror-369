# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check the latency of the latest file available from
GWDataFind for a dataset.
"""

import os
import sys

from dqsegdb2.utils import get_default_host as default_segment_host
from gwdatafind.api.v1 import find_latest_path
from gwdatafind.utils import file_segment
from requests import RequestException

from ..cli import IgwnMonitorArgumentParser
from ..http import (
    get_with_auth,
    make_url,
)
from ..utils import NagiosStatus
from .check_file_latency import check_file_latency
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]


def find_latest(
    host,
    observatory,
    dataset,
    timeout=10,
    urltype=None,
    auth_type="scitoken",
    **request_kw,
):
    path = find_latest_path(observatory, dataset, urltype)
    url = make_url(host, path)

    resp = get_with_auth(auth_type, url, timeout=timeout, **request_kw)
    resp.raise_for_status()

    return resp.json()[0]


def check_gwdatafind_latency(
    host,
    observatory,
    dataset,
    timeout=10,
    flag=None,
    dqsegdb_host=default_segment_host(),
    warning=None,
    critical=None,
    **auth_kw,
):
    # find the URL of the latest file for the chosen dataset
    try:
        latest = find_latest(
            host,
            observatory,
            dataset,
            timeout=timeout,
            **auth_kw,
        )
    except IndexError:  # no files
        return (
            NagiosStatus.CRITICAL,
            f"No files found for {observatory}-{dataset}",
        )
    except RequestException as exc:  # something went wrong
        return (
            NagiosStatus.UNKNOWN,
            os.linesep.join((f"Failed to query {host}", str(exc))),
        )

    # if a 'flag' was specified, use it to set the reference for the
    # latency measurement
    if flag:
        from .check_dqsegdb_latency import (
            NOW,
            find_latest as find_latest_segment_time,
        )
        try:
            now, _ = find_latest_segment_time(
                dqsegdb_host,
                flag,
                file_segment(latest)[1],
                NOW,
                timeout=timeout,
                active=True,
                **auth_kw,
            )
        except IndexError:  # no segments, so report 0 latency
            now = file_segment(latest)[1]
    # otherwise measure against 'NOW'
    else:
        now = None  # use GPS time 'now'

    return check_file_latency(
        latest,
        warning=warning,
        critical=critical,
        now=now,
        disable_find=True,
    )


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
        help="URL/FQDN of gwdatafind host to query",
    )
    parser.add_argument(
        "-o",
        "--observatory",
        metavar="X",
        help="ID for observatory, e.g. 'G' (for GEO)",
    )
    parser.add_argument(
        "-d",
        "--dataset",
        "--frametype",
        dest="dataset",
        help="name of dataset to query, e.g. G1_RDS_C01_L3",
    )
    parser.add_argument(
        "-u",
        "--urltype",
        dest="urltype",
        default=None,
        choices=[None, "file", "https", "osdf"],
        help="type (scheme) of URL to find, defaults to 'any'",
    )
    parser.add_argument(
        "-f",
        "--active-flag",
        dest="flag",
        help="name of flag to use to restrict query time",
    )
    parser.add_argument(
        "-s",
        "--dqsegdb-host",
        default=default_segment_host(),
        help=(
            "address of DQSegDB instance to use when querying "
            "for -f/--active-flag"
        ),
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

    status, message = check_gwdatafind_latency(
        opts.hostname,
        opts.observatory,
        opts.dataset,
        urltype=opts.urltype,
        timeout=opts.timeout,
        flag=opts.flag,
        dqsegdb_host=opts.dqsegdb_host,
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
