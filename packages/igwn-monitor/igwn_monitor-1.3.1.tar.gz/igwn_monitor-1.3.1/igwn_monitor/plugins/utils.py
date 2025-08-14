# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Utilities for IGWN Monitoring Plugins.

Mainly stuff for output formatting.
"""

import json
import subprocess
import sys
import time
from getpass import getuser
from pathlib import Path
from shutil import which
from socket import getfqdn

from ..utils import NagiosStatus


def _git_config(value):
    """Call `git config --get <value>`."""
    git = which("git")
    if not git:
        return
    try:
        return subprocess.run(  # noqa: S603
            [git, "config", "--get", str(value)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        ).stdout.strip().decode("utf-8")
    except OSError:  # failed to execute git
        return None


def user_name():
    """Try and find the current user's name."""
    conf = _git_config("user.name")
    if conf:
        return conf
    try:
        import pwd
    except ModuleNotFoundError:  # Windows
        return getuser()
    return pwd.getpwnam(getuser()).pw_gecos


def user_email():
    """Construct a `user@host` email address for the current user."""
    conf = _git_config("user.email")
    if conf:
        return conf
    return f"{getuser()}@{getfqdn()}"


# -- output formatting ----------------

def write_plugin_output(
    state,
    message,
    file=None,
    format=None,
    **kwargs,
):
    """Write plugin output to a file.

    This hands off to `write_plugin_text` or `write_plugin_json` as
    appropriate.

    Parameters
    ----------
    state : `NagiosStatus`, `int`
        The output state of the plugin being reported.

    message : `str`
        The output message of the plugin.

    file : `str`, `os.PathLike`, `io.IOBase`
        The path or file to write into, defaults to the standard
        output stream (`sys.stdout`).

    format : `str`
        The format to write; if ``format="json"`` is given, or ``file`` has a
        ``".json"`` extension, :func:`write_plugin_json` will be used to write
        output - in all other cases :func:`write_plugin_text` will be used.

    kwargs
        All other keyword arguments will be passed to
        :func:`write_plugin_json`, if writing JSON-format output.
        If writing text output, all other keyword arguments are ignored.

    Returns
    -------
    state : `int`
        The output state of the plugin.
    """
    # default to stdout
    if file is None:
        file = sys.stdout

    # if format not given, determine dynamically
    if format is None:
        # get extension of target file
        if isinstance(file, str):
            path = Path(file)
        elif hasattr(file, "name"):
            path = Path(file.name)
        else:
            path = None

        # translate extension into format
        if path:
            format = path.suffix.lstrip(".")

    # if JSON format or JSON file, write JSON
    if str(format).lower() == "json":
        return write_plugin_json(state, message, file=file, **kwargs)

    # otherwise write text
    return write_plugin_text(state, message, file=file)


def write_plugin_text(
    state,
    message,
    file=None,
):
    if file is None or file == "stdout":
        file = sys.stdout
    if isinstance(file, str):
        with open(file, "w") as fobj:
            return write_plugin_text(state, message, file=fobj)
    print(message, file=file)
    return int(state)


def write_plugin_json(
    state,
    message,
    file=None,
    expiry=None,
    expiry_state=NagiosStatus.UNKNOWN,
    name=None,
    **data,
):
    """Format plugin output for check_json.

    This function formats plugin output in the format expected by the
    :doc:`/plugins/check_json` plugin.

    If ``status_intervals`` is not given as a keyword, this function constructs
    one default interval starting 'now' to report the current state.
    If ``expiry`` is given, a second interval is added to report on expiry of
    the valid state.

    See :doc:`/plugins/json` for details of the supported JSON Schema.

    Parameters
    ----------
    state : `NagiosStatus`, `int`
        The output state of the plugin being reported.

    message : `str`
        The output message of the plugin.

    file : `str`, `pathlib.Path`
        The path to write JSON into.

    expiry : `int`
        The time (in seconds) after which the current state is no longer valid.

    expiry_state : `NagiosStatus`, `int`
        The state to report if the expiry time is reached.

    name : `str`
        The name of the plugin to use when reporting expiry.

    data
        Other key, value pairs to include (verbatim) in the JSON report.
    """
    # set the default created time to NOW
    if not {"created_gps", "created_unix"}.intersection(data):
        data["created_unix"] = int(time.time())

    # set the default user as the running user
    if "author" not in data:
        data["author"] = {
            "name": user_name(),
            "email": user_email(),
        }

    # create intervals
    if "status_intervals" not in data:
        data["status_intervals"] = [{
            "start_sec": 0,
            "num_status": int(state),
            "txt_status": message,
        }]
        if expiry:
            data["status_intervals"][0]["end_sec"] = int(expiry)
            data["status_intervals"].append({
                "start_sec": int(expiry),
                "num_status": int(expiry_state),
                "txt_status": f"{name or 'Monitor'} is not updating",
            })

    # write to file (or stream)
    if file is None or file == "stdout":
        file = sys.stdout
    _write_json(data, file)

    # return what we wrote
    return int(state)


def _write_json(blob, file):
    """Write an object to ``file`` in JSON format."""
    if isinstance(file, str):
        with open(file, "w") as fobj:
            return _write_json(blob, fobj)

    return json.dump(blob, file)
