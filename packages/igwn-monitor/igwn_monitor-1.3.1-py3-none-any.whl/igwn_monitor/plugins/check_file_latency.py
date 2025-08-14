# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check the latency of the most recent file matching a pattern.

Supported schemes:

- |LIGO-T010150|_: the LIGO standard file-naming convention
- "atime": check the last access time of a file
- "ctime": check the metadata change time of a file
- "mtime": check the last modification time of a file
"""

import glob
import os
import sys
from os.path import basename
from pathlib import Path

from gwdatafind.utils import file_segment

from ..cli import IgwnMonitorArgumentParser
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
    from_gps,
    to_gps,
)
from .utils import write_plugin_output

PROG = __name__.rsplit(".", 1)[-1]


# -- schemes --------------------------

def file_end_T010150(path):
    return file_segment(path)[1]


def gps_factory(func):
    """Factory to convert the output of a function from a Unix time to GPS."""
    def gps_func(path):
        return to_gps(func(path))
    return gps_func


FILE_END_FUNC = {
    "T010150": file_end_T010150,
    "atime": gps_factory(os.path.getatime),
    "ctime": gps_factory(os.path.getctime),
    "mtime": gps_factory(os.path.getmtime),
}


# -- file finder ----------------------

def find_latest(path, key=None):
    """Find the latest path in a directory, or matching a pattern."""
    # if path is a directory, search inside it
    if path.is_dir():
        return sorted(path.glob("*"), key=key)[-1]

    # otherwise just resolve the glob
    return sorted(glob.iglob(str(path)), key=key)[-1]


# -- check ----------------------------

def check_file_latency(
    path,
    warning=None,
    critical=None,
    now=None,
    scheme="T010150",
    disable_find=False,
):
    """Check the age of a file as indicated by its filename.

    Parameters
    ----------
    path : `pathlib.Path`
        Path of file or directory or glob pattern to resolve.

    warning : `float`
        Latency (seconds) above which to report ``WARNING``.

    critical : `float`
        Latency (seconds) above which to report ``CRITICAL``.

    now : `float`
        GPS time to use as 'now' when calculating latency, defaults
        to the actual current GPS time.

    scheme : `str`
        Scheme to use when determining age of a file.

    disable_find : `bool`
        If `True`, always treat `path` as the thing to be evaluated,
        and don't attempt to use `glob.glob` to discover the latest file.
        This is mainly useful when using `check_file_latency` to report
        on the latency of a path discovered elsewhere (see
        `check_gwdatafind_latency` for an example).
    """
    file_end = FILE_END_FUNC[scheme]

    # if path isn't a real file, presume it's a directory or a regex
    if not disable_find:
        try:
            path = find_latest(Path(path), key=file_end)
        except IndexError:
            return NagiosStatus.UNKNOWN, f"No files found matching '{path}'"

    # find the end time of the file from the filename
    end = file_end(path)

    # and calculate the latency relative to 'now'
    if now is None:
        now = to_gps("now")
    latency = int(now - end)

    # summarise the result
    summary = f"Latest file ({basename(path)}) is {latency} seconds old"
    perfdata = format_performance_metrics({
        "latency": (f"{latency}s", warning or None, critical or None, 0),
    })
    detail = os.linesep.join((
        f"Full URI: {path}",
        f"File end GPS: {end}",
        f"File end UTC: {from_gps(end)}",
    ))

    message = f"{summary} | {perfdata}{os.linesep}{detail}"

    # set the status according to the latency thresholds
    if critical and latency >= critical:
        return NagiosStatus.CRITICAL, message
    if warning and latency >= warning:
        return NagiosStatus.WARNING, message
    return NagiosStatus.OK, message


# -- command-line running -------------

def create_parser():
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
        add_output_options=True,
        add_timeout=False,  # unsupported
    )
    parser.add_argument(
        "--path",
        "-p",
        required=True,
        help="path to search, e.g. /dev/shm/kafka/H1",
    )
    parser.add_argument(
        "-w",
        "--warning",
        type=float,
        help="latency threshold (in seconds) after which to return WARNING",
    )
    parser.add_argument(
        "-c",
        "--critical",
        type=float,
        help="latency threshold (in seconds) after which to return WARNING",
    )
    parser.add_argument(
        "-s",
        "--scheme",
        choices=FILE_END_FUNC.keys(),
        default="T010150",
        help="scheme to use when evaluating file 'age'",
    )
    parser.add_argument(
        "-n",
        "--now",
        type=float,
        default=to_gps("now"),
        help="GPS time to set as 'now' when calculating latency",
    )
    return parser


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_file_latency(
        opts.path,
        warning=opts.warning,
        critical=opts.critical,
        scheme=opts.scheme,
        now=opts.now,
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
