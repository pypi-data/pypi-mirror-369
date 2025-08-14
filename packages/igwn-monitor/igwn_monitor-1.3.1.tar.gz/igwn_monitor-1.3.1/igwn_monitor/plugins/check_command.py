# Copyright (c) 2024-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check a command suceeds and report as a plugin."""

import argparse
import os
import shutil
import subprocess
import sys
import time

try:
    from shlex import join as shlex_join
except ImportError:  # python < 3.8
    import shlex

    def shlex_join(cmd):
        return " ".join(map(shlex.quote, cmd))

from ..cli import IgwnMonitorArgumentParser
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)
from .utils import write_plugin_output

PROG = __spec__.name.rsplit(".", 1)[-1]


def _run(
    command,
    timeout=None,
    timeout_unknown=False,
    warning=None,
    **kwargs,
):
    # get basename of executable to use in messages
    exe = os.path.basename(command[0])

    # run the command
    try:
        result = subprocess.run(
            command,
            check=False,
            shell=False,
            timeout=timeout,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            **kwargs,
        )
    except OSError as exc:
        return (
            NagiosStatus.UNKNOWN,
            f"Failed to run {exe}",
            str(exc),
        )
    except subprocess.TimeoutExpired:
        return (
            NagiosStatus.UNKNOWN if timeout_unknown else NagiosStatus.CRITICAL,
            f"{exe} timed out",
            "",
        )

    # construct message
    output = result.stdout.decode("utf-8")
    code = result.returncode
    if code:
        message = f"{exe} failed (exited with code {code})"
        if code == warning:
            return NagiosStatus.WARNING, message, output
        return NagiosStatus.CRITICAL, message, output
    return NagiosStatus.OK, f"{exe} succeeded", output


def check_command(
    command,
    verbose=False,
    env=None,
    timeout=None,
    timeout_unknown=False,
    warning=None,
    **kwargs,
):
    """Run a command in a subprocess and process the result.

    Parameters
    ----------
    command : `list`
        The command to run in the subprocess, as a list of
        arguments and options.

    verbose : `bool`
        If `True`, include the command string and all output in the response.

    warning : `int`
        A non-zero returncode to interpret as ``WARNING``.
        All other non-zero responses will be reported as ``CRITICAL``.

    timeout_unknown : `bool`
        If `True`, return ``UNKNOWN`` in the event of a timeout, otherwise
        return ``CRITICAL`` (default).

    kwargs
        All other keyword arguments are passed to :func:`subprocess.run`.

    Returns
    -------
    status : `NagiosStatus`
        The Nagios status code

    message : `str`
        The reponse from the check.

    Notes
    -----
    The return status will be as follows

    - ``OK`` (0) - if the command returned an exit code of 0
    - ``WARNING`` (1) - if the command returned a non-zero exit code
      matching the ``warning`` argument
    - ``CRITICAL`` (2) - if the command returned a non-zero exit code
      not matching ``warning``, OR

    See also
    --------
    subprocess.run
    """
    # try and get absolute path of executable
    command[0] = shutil.which(command[0]) or command[0]

    # record time now
    start = time.time()

    status, message, output = _run(
        command,
        env=env,
        timeout=timeout,
        timeout_unknown=timeout_unknown,
        warning=warning,
        **kwargs,
    )
    runtime = time.time() - start

    # add runtime as performance data
    perfdata = {"runtime": (round(runtime, 3), timeout, timeout, 0, timeout)}
    message += f" | {format_performance_metrics(perfdata, unit='s')}"

    # append stdout or stderr
    if verbose:
        prompt = ">" if os.name == "nt" else "$"
        cmdstr = shlex_join(command)
        message += os.linesep.join((
            "",  # leading linesep
            f"{prompt} {cmdstr}",
            output,
        )).rstrip()

    return status, message


def create_parser():
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
        add_output_options=True,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="include command output in plugin response",
    )
    parser.add_argument(
        "-T",
        "--timeout-unknown",
        action="store_true",
        default=False,
        help="return UNKNOWN in the event of a timeout",
    )
    parser.add_argument(
        "-w",
        "--warning-code",
        default=None,
        type=int,
        help="Non-zero exit code to return as WARNING",
    )
    cmdparser = parser.add_argument_group(
        "Command arguments",
    )
    cmdparser.add_argument(
        "-U",
        "--empty-env",
        action="store_true",
        default=False,
        help="empty the environment before running the command",
    )
    cmdparser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="remaining arguments are parsed as the command to check",
    )
    return parser


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message = check_command(
        opts.command,
        timeout=opts.timeout,
        timeout_unknown=opts.timeout_unknown,
        env={} if opts.empty_env else None,
        verbose=opts.verbose,
        warning=opts.warning_code,
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
