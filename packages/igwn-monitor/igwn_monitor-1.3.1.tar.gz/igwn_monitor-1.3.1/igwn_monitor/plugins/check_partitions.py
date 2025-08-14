# Copyright (c) 2023-2025 Cardiff University
#               2023 University of Wisconsin-Milwaukee
# SPDX-License-Identifier: MIT

"""Check the status of a DMT partition."""

import re
import subprocess
import sys
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from shutil import which

from ..cli import IgwnMonitorArgumentParser
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]

# the output of smlatency is lines like
# "Partition X1THING_Data latency, n=1,  avg=12.34  sig=0  max=12.34"
SMLATENCY_OUTPUT = re.compile(
    r"\APartition (?P<partition>[\w]+) latency, "
    r"n=(?P<num>\d+)  avg=(?P<average>[0-9\.]+)  "
    r"sig=([0-9\.]+)  max=(?P<max>[0-9\.])",
)


def check_partition(
    partition,
    warning=None,
    critical=None,
    timeout=8,
):
    """Run ``smlatency --average 1 <partition>`` to determine the
    latency of a DMT Shared Memory Partition.

    Returns
    -------
    latency : `float
        the latency in seconds of the partition

    max : `float`
        the maximum latency as calculated over the number of averages

    gpstime : `float`
        the GPS time of the latest SM buffer
    """
    cmd = [
        which("smlatency"),
        "--average", "1",
        str(partition),
    ]
    try:
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=True,
        )
    except subprocess.TimeoutExpired as exc:
        out = exc.output.decode("utf-8")
        params = SMLATENCY_OUTPUT.match(out).groupdict()

        # if we get here, then smlatency worked and gave sane output
        # so use `smstat last_ID <partition>` to get the GPS time of
        # the latest buffer segment
        gpstime = float(subprocess.check_output(
            [which("smstat"), "last_ID", str(partition)],
        ))
        return float(params["average"]), float(params["max"]), gpstime
    msg = "smlatency didn't timeout, something went wrong"
    raise RuntimeError(msg)


def check_partitions(
    *partitions,
    warning=None,
    critical=None,
    timeout=8.,
    nthreads=None,
):
    """Check the latency of one or more DMT shared memory partitions."""
    nthreads = nthreads or len(partitions)
    latencies = {}
    status = NagiosStatus.OK
    with ThreadPoolExecutor(max_workers=nthreads) as executor:
        futures = {executor.submit(
            check_partition,
            partition,
            timeout=timeout,
        ): partition for partition in partitions}
        for future in as_completed(futures):
            partition = futures[future]
            try:
                latency = future.result()
            except subprocess.CalledProcessError as exc:
                status = max(status, NagiosStatus.CRITICAL)
                latencies[partition] = exc.stderr.decode("utf-8").strip()
            except Exception as exc:
                status = max(status, NagiosStatus.CRITICAL)
                latencies[partition] = str(exc)
            else:
                latencies[partition] = latency

    for latency in latencies.values():
        if not isinstance(latency, float):
            continue
        lat, max_, gps = latency
        if critical and max_ >= critical:
            status = max(status, NagiosStatus.CRITICAL)
        elif warning and max_ >= warning:
            status = max(status, NagiosStatus.WARNING)

    # format latency for each partition as performance data
    perfdata_params = (warning or "", critical or "", 0., critical or "")
    perfdata = {
        f"latency_{part}": (latency[0],) + perfdata_params
        for part, latency in latencies.items() if not isinstance(latency, str)
    }
    perfdatastr = format_performance_metrics(perfdata, unit="s")

    # generate the plugin status message
    if len(partitions) == len(perfdata):  # all partitions found
        message = f"Latency {status.name}: " + "; ".join(
            f"{part}={latency[0]}s ({latency[2]})"
            for part, latency in latencies.items()
        )
    else:  # something failed
        message, = (val for val in latencies.values() if isinstance(val, str))

    # append performance data, if we got some
    if perfdatastr:
        message += f" | {perfdatastr}"

    return status, message


def create_parser():
    """Create an argument parser for this script."""
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
        add_output_options=True,
        add_timeout=10.,
    )
    parser.add_argument(
        "-P",
        "--part",
        "--partition",
        dest="partitions",
        required=True,
        action="append",
        help="partition to check",
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
    return parser


def main(args=None):
    """Run the thing."""
    parser = create_parser()
    opts = parser.parse_args(args=args)
    status, message = check_partitions(
        *opts.partitions or [],
        warning=opts.warning,
        critical=opts.critical,
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
