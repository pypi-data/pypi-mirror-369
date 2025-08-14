# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

import os
import sys

from dqsegdb2.query import query_segments
from gwdatafind.ui import find_times
from igwn_segments import (
    segment as Segment,
    segmentlist as SegmentList,
)
from requests import (
    HTTPError,
    RequestException,
)

from ..auth import auth_context
from ..cli import IgwnMonitorArgumentParser
from ..http import response_message
from ..utils import (
    NagiosStatus,
    from_gps,
    to_gps,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

NOW = int(to_gps("now"))


def check_data_availability(
    start,
    end,
    observatory,
    dataset,
    flag=None,
    veto=None,
    dqsegdb_host=None,
    gwdatafind_host=None,
    timeout=10,
    auth_type="none",
    **auth_kw,
):
    search = SegmentList([Segment(start, end)])

    with auth_context(auth_type, **auth_kw):
        try:
            data_segs = find_times(
                observatory,
                dataset,
                gpsstart=start,
                gpsend=end,
                host=gwdatafind_host,
                timeout=timeout,
            )

            if flag:
                search &= query_segments(
                    flag,
                    start,
                    end,
                    host=dqsegdb_host,
                    timeout=timeout,
                )["active"]
            for vflag in veto or []:
                search -= query_segments(
                    vflag,
                    start,
                    end,
                    host=dqsegdb_host,
                    timeout=timeout,
                )["active"]
        except HTTPError as exc:  # something went wrong
            return NagiosStatus.UNKNOWN, response_message(exc.response)
        except RequestException as exc:  # something else went wrong
            return NagiosStatus.UNKNOWN, str(exc)

    if not data_segs:
        return (
            NagiosStatus.CRITICAL,
            f"No data found for {observatory}-{dataset}",
        )

    # pin the 'search' to the extent of the data to not report a 'gap'
    # simply due to latency
    search &= SegmentList([data_segs.extent()])

    # find the gaps
    gaps = search - data_segs

    # remove gap up to 'now' due to latency
    if len(gaps) and gaps[-1][1] >= NOW:
        gaps.pop(-1)

    # if gaps, present a summary of the gaps
    if gaps:
        def format_gap(seg):
            return (
                f"  {from_gps(seg[0])}"
                f" .. {from_gps(seg[1])}"
                f"  ({int(abs(seg))}s)"
            )

        total = abs(gaps)
        message = os.linesep.join((
            f"Gaps found in data availability ({total}s)",
            "Gaps (UTC):",
            "  {}".format("\n  ".join(map(format_gap, gaps))),
            "Segments:",
        ) + tuple(f"{int(seg[0])} {int(seg[1])}" for seg in gaps))
        return NagiosStatus.WARNING, message

    return NagiosStatus.OK, "No data availability gaps found"


def search_time(value):
    value = int(value)
    if value > 0:
        return value
    return NOW + value


def create_parser():
    """Create an argument parser for this script."""
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
        add_output_options=True,
    )
    parser.add_argument(
        "-o",
        "--observatory",
        help="observatory prefix",
    )
    parser.add_argument(
        "-d",
        "--dataset",
        "--frametype",
        help="dataset name to search for"
    )
    parser.add_argument(
        "-s",
        "--start-time",
        default=search_time(-86400),
        type=search_time,
        help="GPS start time, give <=0 for 'time from now'",
    )
    parser.add_argument(
        "-e",
        "--end-time",
        default=search_time(0),
        type=search_time,
        help="GPS end time, give <=0 for 'time from now'",
    )
    parser.add_argument(
        "-A",
        "--analysis-flag",
        help="name of analysis flag for inclusion segments",
    )
    parser.add_argument(
        "-F",
        "--veto-flag",
        action="append",
        help="name of veto flag for exclusion segments",
    )
    parser.add_argument(
        "-H",
        "--gwdatafind-host",
        default="https://datafind.ligo.org",
        help="address of GWDataFind server",
    )
    parser.add_argument(
        "-Z",
        "--dqsegdb-host",
        default="https://segments.ligo.org",
        help="address of DQSegDB server",
    )
    parser.add_auth_argument_group()
    return parser


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_data_availability(
        opts.start_time,
        opts.end_time,
        opts.observatory,
        opts.dataset,
        opts.analysis_flag,
        timeout=opts.timeout,
        veto=opts.veto_flag,
        dqsegdb_host=opts.dqsegdb_host,
        gwdatafind_host=opts.gwdatafind_host,
        auth_type=opts.auth_type,
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
