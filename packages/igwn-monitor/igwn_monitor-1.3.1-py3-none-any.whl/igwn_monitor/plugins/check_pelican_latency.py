# Copyright (c) 2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Check the latency of the latest file available from a Pelican federation."""

import fnmatch
import glob
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from ..auth import auth_context
from ..cli import IgwnMonitorArgumentParser
from ..compat import shlex_join
from ..utils import NagiosStatus
from .check_file_latency import check_file_latency
from .utils import write_plugin_output

log = logging.getLogger(__name__)

PELICAN = shutil.which("pelican") or "pelican"
PROG = __name__.rsplit(".", 1)[-1]


def run_pelican(
    *args,
    check=True,
    **kwargs,
):
    """Run ``pelican`` with arguments.

    Parameters
    ----------
    args
        All positional arguments are passed as arguments to
        ``pelican object ls``.

    check : `bool`, optional
        Whether to raise an exception is the command fails.
        Default is `True`.

    kwargs
        All keyword arguments are passed to `subprocess.run`.

    Returns
    -------
    stdout : `str`
        The captured standard output from the process.

    Raises
    ------
    subprocess.CalledProcessError
        If the call to ``pelican`` fails (returns exit code != 0).
    """
    cmd = [PELICAN, *args]
    cmdstr = shlex_join(cmd)
    log.debug("$ %s", cmdstr)
    return subprocess.run(cmd, check=check, **kwargs).stdout


def pelican_ls(
    path,
    federation=None,
    token=None,
    timeout=60,
):
    """Run ``pelican object ls``.

    Parameters
    ----------
    path : `str`
        The path to list.

    federation : `str`
        The URL of the federation that provides ``path``.
        Passed as the ``--federation`` argument to ``pelican object ls``.

    token : `str`
        The path of the token file to use for authorising the transfer.
        Passed as the ``--token`` argument to ``pelican object ls``.

    timeout : `int`, optional
        The number of seconds to wait for a response from Pelican before aborting.

    Returns
    -------
    paths : `list` of `str`
        The parsed JSON output from ``pelican object ls``, which _should be_
        a `list` of `str` representing discovered paths under ``path``.
    """
    args = [
        "object",
        "ls",
        "--json",
        str(path),
    ]
    if log.isEnabledFor(logging.DEBUG):
        args.append("--debug")
    if federation:
        args.extend(("--federation", federation))
    if token:
        args.extend(("--token", token))
    return json.loads(run_pelican(
        *args,
        stdout=subprocess.PIPE,
        timeout=timeout,
    ))


def pelican_iglob(
    pathname,
    federation=None,
    token=None,
    *,
    ordered_dirs=False,
    timeout=60,
):
    """Recursively glob for a path/pattern from a Pelican federation.

    Parameters
    ----------
    pathname : `str`, `pathlib.Path`
        The path or pattern to glob.

    federation : `str`
        The URL of the federation that provides ``path``.
        Passed as the ``--federation`` argument to ``pelican object ls``.

    token : `str`
        The path of the token file to use for authorising the transfer.
        Passed as the ``--token`` argument to ``pelican object ls``.

    ordered_dirs : `bool`
        If `True`, presume that directory names can be sorted and only
        recurse into the sorted-last directory at each level.
        Default is `False`.

    timeout : `int`, optional
        The number of seconds to wait for a response from Pelican before aborting.

    Yields
    ------
    path : `str`
        The path of a file in the Pelican federation matching the
        ``pathname`` pattern.
    """
    path = Path(pathname)
    parent = path.parent
    basename = path.name
    if glob.has_magic(str(parent)):
        dirs = list(pelican_iglob(
            parent,
            federation=federation,
            token=token,
            timeout=timeout,
        ))
    else:
        dirs = [parent]

    if ordered_dirs:
        log.debug("Selecting last directory by name")
        dirs = [sorted(dirs)[-1]]

    for dirname in dirs:
        log.debug("Listing %s", dirname)
        dirlist = pelican_ls(
            dirname,
            federation=federation,
            token=token,
            timeout=timeout,
        )
        for entry in dirlist:
            if not fnmatch.fnmatchcase(entry, basename):
                continue
            yield os.path.join(dirname, entry)


def check_pelican_latest(
    pattern,
    federation=None,
    ordered_dirs=None,
    warning=None,
    critical=None,
    timeout=60,
    auth_type=None,
    **auth_kw,
):
    """Check the latest file available in a Pelican federation.

    Parameters
    ----------
    pattern : `str`, `pathlib.Path`
        The path or pattern to glob.

    federation : `str`, optional
        The URL of the federation that provides ``path``.
        Passed as the ``--federation`` argument to ``pelican object ls``.

    ordered_dirs : `bool`, optional
        If `True`, presume that directory names can be sorted and only
        recurse into the sorted-last directory at each level.
        Default is `False`.

    warning : `int`, optional
        The latency (age, in seconds) above which to report ``WARNING``.

    critical : `int`, optional
        The latency (age, in seconds) above which to report ``CRITICAL``.

    timeout : `int`, optional
        The number of seconds to wait for a response from Pelican before aborting.

    auth_type : `str`, optional
        The type of authentication/authorisation to use when talking to
        the Pelican federation. Only ``"none"`` and ``"scitoken"`` are
        accepted.

    auth_kw
        All other keyword arguments are passed to
        :func:`igwn_monitor.auth.auth_context`.

    Returns
    -------
    status: `int`
        The `NagiosStatus` code for this response.

    message : `str`
        The plugin check message to be displayed.
    """
    with auth_context(auth_type, **auth_kw):
        try:
            files = sorted(pelican_iglob(
                pattern,
                federation=federation,
                ordered_dirs=ordered_dirs,
                token=os.getenv("BEARER_TOKEN_FILE"),
                timeout=timeout,
            ))
        except subprocess.SubprocessError as exc:
            if isinstance(exc, subprocess.TimeoutExpired):
                msg = "Pelican query timed out"
            else:
                msg = "Pelican query failed"
            if isinstance(exc.cmd, list):  # for pretty printing
                exc.cmd = shlex_join(exc.cmd)
            return (
                NagiosStatus.UNKNOWN,
                os.linesep.join((msg, str(exc))),
            )

    # keep only the path of the file
    # (replacing leading double slash with single)
    try:
        latest = f"/{urlparse(files[-1]).path.lstrip('/')}"
    except IndexError:
        return (
            NagiosStatus.UNKNOWN,
            f"No files found for query '{pattern}'",
        )

    return check_file_latency(
        latest,
        warning=warning,
        critical=critical,
        disable_find=True,
    )


def create_parser():
    """Create an `argparse.ArgumentParser` for this tool."""
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=PROG,
        add_output_options=True,
    )
    parser.add_argument(
        "-g",
        "--pattern",
        metavar="GLOB",
        required=True,
        help="Glob-style pattern for which to search",
    )
    parser.add_argument(
        "-f",
        "--federation",
        help="URL of Pelican Federation",
    )
    parser.add_argument(
        "-o",
        "--ordered-dirs",
        action="store_true",
        default=False,
        help=(
            "Presume that globbed directories can be ordered and that the "
            "last directory in order contains the most recent data"
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
    parser.add_auth_argument_group(
        auth_type=("none", "scitoken"),
    )
    return parser


def main(args=None):
    """Run the plugin."""
    parser = create_parser()
    opts = parser.parse_args(args=args)
    status, message = check_pelican_latest(
        opts.pattern,
        federation=opts.federation,
        ordered_dirs=opts.ordered_dirs,
        warning=opts.warning,
        critical=opts.critical,
        timeout=opts.timeout,
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
