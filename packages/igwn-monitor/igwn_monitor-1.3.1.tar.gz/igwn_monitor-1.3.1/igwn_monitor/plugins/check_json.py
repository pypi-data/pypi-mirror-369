# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Access a JSON artifact via HTTP(S) and interpret for Icinga.

This script natively handles various types of IGWN Auth.

The JSON Schema that defines the format for valid JSON input files is
available from

https://git.ligo.org/computing/monitoring/igwn-monitoring-plugins/-/tree/main/igwn_monitor/plugins/check_json_schema.json

This is summarised online :doc:`here <json>`.
"""

import argparse
import functools
import getpass
import hashlib
import json
import logging
import math
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    import importlib.resources as importlib_resources
except ModuleNotFoundError:
    import importlib_resources

import requests

# ECP (Shibboleth, via Kerberos)
from ciecplib.cookies import (
    ECPCookieJar,
    load_cookiejar,
)
from jsonschema import (
    ValidationError,
    validate as validate_json,
)

from .. import __version__
from ..cli import IgwnMonitorArgumentParser
from ..http import get_with_auth
from ..logging import init_logging
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
    from_gps,
)

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"
__credits__ = "Patrick Brockill"

ANSI_COLOR_CODES_REGEX = re.compile(
    r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]",
)
HTML_REGEX = re.compile(r"<\w+(?:\s\w+=[^>]*)?>")

PROG = "nagios-check-json"

try:
    SCHEMA = json.loads(importlib_resources.files(__package__).joinpath(
        "check_json_schema.json",
    ).read_text())
except AttributeError:  # python < 3.9
    SCHEMA = json.loads(importlib_resources.read_text(
        __package__,
        "check_json_schema.json",
    ))

# update hyperlink for JSON Schema to use exact tag
if "dev" not in __version__:
    __doc__ = __doc__.replace("tree/main", f"tree/{__version__}")
    SCHEMA["$id"] = SCHEMA["$id"].replace("raw/main", f"raw/{__version__}")


# -- utilities --------------

@functools.lru_cache(64)
def md5_hex(in_):
    """Construct the MD5 hex digest for a string.

    Parameters
    ----------
    in_ : `str`
        The input string to encode.

    Returns
    -------
    digest : `str`
        The hash digest in hexadecimal form.
    """
    inbytes = in_.encode("utf-8")
    try:
        return hashlib.md5(
            inbytes,
            usedforsecurity=False,
        ).hexdigest()
    except TypeError:  # python < 3.9
        return hashlib.md5(inbytes).hexdigest()  # noqa: S324


def default_cookie_file(target):
    """Determine the default value for --cookie-file for the given target URL.

    Parameters
    ----------
    target : `str`
        The URL that will be accessed, or at least the fully-qualified
        host name.

    Returns
    -------
    cookie_file : `pathlib.Path`
        The default cookie file path to use when accessing this URL,
        whose parent directory may not exist yet.
    """
    tmpdir = Path(tempfile.gettempdir())
    name = f"{getpass.getuser()}_cookies_{urlparse(target).hostname}"
    return tmpdir / name


def default_cache_dir():
    """Determine the default value for --cache-dir.

    Returns
    -------
    cache_dir : `pathlib.Path`
        The default cache directory path (which may not exist yet).
    """
    if getpass.getuser() in ("root", "nobody"):
        base = Path("/var") / "lib"
    else:
        base = Path.home() / ".cache"
    return base / PROG


def cache_file(base, target):
    """Determine the cache file to use for the target URL.

    Parameters
    ----------
    base : `str`, `pathlib.Path`
        The base cache directory in which to cache for this URL.

    target : `str`
        The target URL whose contents will be cached.

    Returns
    -------
    cache_file : `pathlib.Path`
        The cache file path to use for the target URL.
    """
    md5 = md5_hex(target)
    return Path(base) / md5 / "status.json"


def default_log_dir():
    """Return the default base log directory.

    Returns
    -------
    log_dir : `pathlib.Path`
        The default log directory path (which may not exist yet).
    """
    if getpass.getuser() in ("root", "nobody"):
        return Path("/var") / "log" / PROG
    return Path.home() / ".cache" / PROG / "log"


def log_file(base, target):
    """Return the log file path to use for logging interactions with
    the target URL.

    Parameters
    ----------
    base : `str`, `pathlib.Path`
        The base log directory in which to write logs for this URL.

    target : `str`
        The target URL whose interactions will be logged.

    Returns
    -------
    log_file : `pathlib.Path`
        The log file path to use for the target URL.
    """
    # allow user to specify to log directly to console
    if str(base) in ("stdout", "stderr"):
        return str(base)
    # otherwise configure a unique log directory for this URL
    md5 = md5_hex(target)
    return Path(base) / md5 / "transaction.log"


def sanitise_text(text):
    """Sanitised a block of text by removing unsupported characters."""
    for regex in (
        ANSI_COLOR_CODES_REGEX,
    ):
        text = regex.sub("", text)
    return text


def parse_json(response, logger):
    """Parse JSON from a `requests.Response`.

    This function first attemps to parse JSON from a response object as normal,
    then tries again with a sanitised version.

    The sanitisation attemps to remove non-ASCII characters such as ASNI escape
    codes.
    """
    # first, parse as normal
    try:
        return response.json()
    except json.JSONDecodeError as exc:
        logger.warning(f"Parsing JSON failed: {exc}")
        # try again with a sanitised version
        try:
            data = json.loads(sanitise_text(response.text))
            logger.debug("Parsed sanitised JSON")
            return data
        except json.JSONDecodeError:
            # didn't work, raise the original error
            pass

        # if we got something that wasn't JSON, add that to the message
        content_type = response.headers.get("content-type")
        if not content_type.startswith("application/json"):
            exc.args = (
                str(exc) + f" [content-type is {content_type}]",
            )
        raise


# -- HTTP request handling --

def get_json(
    target,
    logger,
    timeout=30.,
    auth_type="any",
    cache=None,
    **session_kw
):
    """Retrieve JSON data from the target URL.

    Parameters
    ----------
    target : `str`
        The URL to ``GET``, must be HTTP or HTTPS.

    logger : `logging.Logger`
        The logger to emit progress messages to.

    timeout : `float`
        Time (seconds) before connection attempt should time out.

    auth_type : `str`
        The authorization scheme to use

    cache : `str`, `pathlib.Path`
        The file in which to cache the result.

    krb_keytab : `str`, `pathlib.Path`
        The path of a Kerberos keytab file, if available.

    krb_ccache : `str`, `pathlib.Path`
        The path to use as the credential cache when discovering or
        creating new credentials.

    **session_kw
        All other keyword arguments are passed along to the `Session`.

    Returns
    -------
    data : `object`
        The object that represents the data parsed as JSON from the
        ``target`` URL.
    """
    # local file
    if str(target).startswith("file://") or os.path.isfile(target):
        raw, data = _get_json_file(target)
    # remote file
    else:
        raw, data = _get_json_url(
            target,
            logger,
            timeout=timeout,
            auth_type=auth_type,
            **session_kw,
        )

    logger.debug(f"Received data from {target}")

    # save a copy of the file in a cache
    if cache is not None:
        cache.parent.mkdir(parents=True, exist_ok=True)
        with cache.open("wb") as file:
            file.write(raw)
        logger.debug(f"Cached JSON to {cache}")

    return data


def _get_json_file(target):
    """Get JSON from a local file.

    This is mainly useful for testing.
    """
    if str(target).startswith("file://"):
        target = str(target)[7:]
    with open(target, "rb") as file:
        raw = file.read()
        data = json.loads(raw)
    return raw, data


def _get_json_url(
    target,
    logger,
    timeout=30.,
    auth_type="any",
    cookiefile=None,
    **session_kw,
):
    """Get JSON from a remote URL."""
    # try and load existing cookies
    if cookiefile:
        session_kw["cookiejar"] = load_cookiejar(cookiefile, strict=False)
        ncook = len(session_kw["cookiejar"])
        logger.debug(f"Loaded {ncook} cookies from {cookiefile}")

    resp = get_with_auth(
        auth_type,
        target,
        timeout=timeout,
        **session_kw,
    )
    resp.raise_for_status()
    try:
        data = parse_json(resp, logger)
    finally:
        # store the cookies so that they may be reused next time
        if cookiefile:
            Path(cookiefile).parent.mkdir(parents=True, exist_ok=True)
            jar = ECPCookieJar()
            jar.update(resp.cookies)
            jar.save(
                cookiefile,
                ignore_discard=True,
                ignore_expires=True,
            )
            logger.debug(f"Cached {len(jar)} cookies to {cookiefile}")

    return resp.content, data


def load_json(path):
    """Load JSON from a path.

    Parameters
    ----------
    path : `str`, `pathlib.Path`
        The file path from which to read.

    Returns
    -------
    data : `object`
        The object that represents the data parsed as JSON from the file.
    """
    with Path(path).open("r") as file:
        return json.load(file)


# -- JSON parsing/formatting

def elapsed_time(data):
    """Determine the time elapsed since the JSON file was created.

    This compares the ``'created_unix'`` or ``'created_gps'`` keys
    in the JSON data to the current Unix time, and returns the
    difference.

    If no ``'created_xxx'`` key is found, the return value will be
    ``1`` (one second).

    Parameters
    ----------
    data : `dict`
        The JSON blob representing a service status.
    """
    now = time.time()
    try:
        created = float(data["created_unix"])
    except KeyError:
        try:
            created = from_gps(float(data["created_gps"])).timestamp()
        except KeyError:
            # default to created one-second-ago
            return 1
    return int(now - created)


def status_interval(data):
    """Find and return the relevant status interval.

    This is based on the ``'start_sec'`` and ``'end_sec'`` keys in each
    of the ``'status_interval'`` mappings. The first valid interval is
    returned immediately (i.e. there is no protection against duplicate
    or overlapping intervals).

    Parameters
    ----------
    data : `dict`
        The JSON blob representing a service status.
    """
    elapsed = elapsed_time(data)
    for interval in sorted(
        data["status_intervals"],
        key=lambda x: x.get("start_sec", 0),
        reverse=True,
    ):
        if (
            float(interval.get("start_sec", 0)) <= elapsed
            and float(interval.get("end_sec", math.inf)) >= elapsed
        ):
            return interval
    msg = f"No status_interval matches elapsed time [{elapsed}]"
    raise ValueError(msg)


def _epilog_legend(data):
    """Construct an epilogue string that acts as a legend for the report.

    Parameters
    ----------
    data : `dict`
        The JSON blob representing a service status.

    Returns
    -------
    epilog : `str`
        An HTML formatted block of text to append to the report text.
    """
    lines = []
    for key, color in [
        ("ok_txt", "#44BB77"),
        ("warning_txt", "#FFAA44"),
        ("critical_txt", "#FF5566"),
        ("unknown_txt", "#AA44FF"),
    ]:
        status = key.split("_", 1)[0].upper()
        if key in data:
            lines.append(
                f"  <font color='{color}'>{status}</font>: {data[key]}",
            )
    if lines:
        lines.insert(0, "Status Legend:")
    return "\n".join(lines)


def _epilog_author(data):
    """Construct an epilogue string that describes the authors of the report.

    Parameters
    ----------
    data : `dict`
        The JSON blob representing a service status.

    Returns
    -------
    epilog : `str`
        An HTML formatted block of text to append to the report text.
    """
    lines = []
    authors = data.get("author", {})
    if not isinstance(authors, list):
        authors = [authors]
    for author in authors:
        if isinstance(author, dict):
            name = author.get("name", None)
            addr = author.get("email", None)
        else:
            name = str(author)
            addr = None
        if addr:
            addr = f"<a href=\"mailto:{addr}\">{addr}</a>"
        if name and addr:
            lines.append(f"Author: {name} ({addr})")
        elif name:
            lines.append("Author: " + name)
    return "\n".join(lines)


def _epilog_origin(origin):
    """Construct an epilogue string linking back to the origin of the report."""
    if not origin:
        return
    if urlparse(origin).scheme in ("http", "https"):
        return f"Origin: <a href=\"{origin}\" target=\"_blank\">{origin}</a>"
    return f"Origin: {origin}"


def status_epilog(data, origin):
    """Construct the epilogue for this report.

    The epilogue is additional useful text that is appended to the
    ``txt_status`` for the relevant status interval.

    This text will be independent of the reported status of the service.

    Parameters
    ----------
    data : `dict`
        The JSON blob representing a service status.

    Returns
    -------
    epilog : `str`
        An HTML formatted block of text to append to the report text.
    """
    lines = []
    for func in (
        _epilog_legend,
        _epilog_author,
    ):
        lines.append(func(data))
    lines.append(_epilog_origin(origin))
    # join all non-empty lines
    return "\n".join(filter(None, lines))


def _report_error(error):
    """Format an `Exception` to act at the service status.

    Parameters
    ----------
    error : `Exception`
        The `Exception` to inspect.

    stream : `file`, optional
        The file stream to print to, defaults to `sys.stdout`.

    Returns
    -------
    status : `NagiosStatus`
        The `NagiosStatus` enum value, currently always `NagiosStatus.UNKNOWN`.
    """
    if isinstance(error, json.JSONDecodeError):
        error = f"Failed to parse JSON: {error}"
    elif "kerberos" in str(error).lower():
        error = f"Authorisation failed: {error}"
    if not error:
        error = "Unknown error"
    return NagiosStatus.UNKNOWN, str(error), None


def _format_for_html(text):
    return f"<div style=\"white-space: pre;\">{text}{os.linesep}</div>"


def format_for_html(message, epilog):
    ishtml = any(map(HTML_REGEX.search, (message, epilog)))
    if not ishtml:
        return message, epilog

    # format each block
    message = _format_for_html(message)
    epilog = _format_for_html(epilog)

    # if printing an epilog, separate it with <hr>
    if epilog:
        epilog = "<hr>" + os.linesep + epilog

    return message, epilog


def report_nagios(data, origin, error=None):
    """Format JSON data as a service status report.

    Parameters
    ----------
    data : `dict`
        The JSON data to format.

    origin : `str`
        The URL from which these data were retrieved.

    error : `Exception`, optional
        An `Exception` that was caught along the way, if appropriate.

    stream : `file`, optional
        The file stream to print to, defaults to `sys.stdout`.

    Returns
    -------
    status : `NagiosStatus`
        The `NagiosStatus` enum value parsed from the JSON data.
        If ``error`` is given the returned status will
        always be `NagiosStatus.UNKNOWN`.
    """
    # something went wrong, nothing was received or read from the cache
    if error:
        errorstatus = _report_error(error)
        if not data:
            return errorstatus

    # if we get here, we should have data
    try:
        interval = status_interval(data)
    except KeyError as exc:
        error = ValueError(f"Failed to parse JSON: missing key '{exc}'")
        return _report_error(error)
    except ValueError as exc:
        return _report_error(exc)

    status = NagiosStatus(interval.get("num_status", NagiosStatus.UNKNOWN))
    message = interval.get(
        "txt_status",
        status.name,
    ).replace("\\n", "\n")
    detail = status_epilog(data, origin)
    metrics = format_performance_metrics(data.get("performance_metrics", {}))

    if error:
        status, emessage, edetail = errorstatus
        detail = "\n".join((
            "The following status was taken from the cache:",
            message,
            detail,
        ))
        message = emessage
    if metrics:
        message += "|" + metrics

    # if we received HTML, format line breaks for HTML
    message, detail = format_for_html(message, detail)

    return (
        status,
        message,
        detail,
    )


# -- check function ---------

def check_json(
    url,
    auth_type="any",
    cache=None,
    logger=None,
    logfile=None,
    verbose=False,
    timeout=10.,
    **request_kw,
):
    """Grab JSON from a URL and use it to report a check status as a plugin."""
    # init logging
    if logger is None:
        logger = init_logging(
            name=PROG,
            level=logging.DEBUG if verbose else logging.INFO,
            stream=logfile,
        )

    # get JSON
    logger.debug(f"Fetching {url}")
    try:
        data = get_json(
            url,
            logger,
            auth_type=auth_type,
            cache=cache,
            timeout=timeout,
            **request_kw,
        )
    except (
        OSError,  # local file issue
        json.JSONDecodeError,  # JSON parsing issue
        requests.RequestException,  # remote URL issue
    ) as exc:
        error = exc
        logger.warning(f"Caught {type(exc).__name__}: {exc}:")

        # load cached version of data
        try:
            data = load_json(cache)
        except FileNotFoundError:  # no cache
            return (
                NagiosStatus.UNKNOWN,
                str(exc),
                None,
            )
    else:
        error = None

    try:
        validate_json(instance=data, schema=SCHEMA)
    except ValidationError as exc:
        return (
            NagiosStatus.UNKNOWN,
            "JSON failed validation against the schema",
            str(exc.message),
        )

    # parse the JSON and print to console
    status, message, detail = report_nagios(data, url, error=error)

    # log the file status
    {
        NagiosStatus.OK: logger.debug,
        NagiosStatus.WARNING: logger.warning,
        NagiosStatus.CRITICAL: logger.critical,
        NagiosStatus.UNKNOWN: logger.warning,
    }.get(status, logger.warning)(f"Parsed status {status.name}")

    # and exit
    return status, message, detail


# -- command-line parsing ---

class JsonSchemaAction(argparse.Action):
    def __call__(self, parser, *args, **kwargs):
        json.dump(SCHEMA, sys.stdout, indent=2)
        parser.exit()


def create_parser():
    """Create an `~argparse.ArgumentParser` for this tool.

    Returns
    -------
    parser : `argparse.ArgumentParser`
        The parser to use when parsing command-line arguments.
    """
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=__name__.rsplit(".", 1)[-1],
        add_timeout=True,
        add_output_options=False,  # don't need that here
    )

    parser.add_argument(
        "-u",
        "--url",
        metavar="http-address-to-scrape",
        help="URL to GET via HTTP(S)",
    )
    parser.add_argument(
        "-c",
        "--cache-dir",
        default=default_cache_dir(),
        type=Path,
        help="base directory to use for cache",
    )

    authargs = parser.add_auth_argument_group(kerberos=True)
    authargs.add_argument(
        "-F",
        "--cookie-file",
        type=Path,
        default=argparse.SUPPRESS,
        help=(
            "cookie file to use for query "
            "(default: /tmp/${user}_cookies_${http-address-to-scape})"
        ),
    )
    parser.add_argument(
        "-l",
        "--log-dir",
        default=default_log_dir(),
        type=Path,
        help="base directory to use for log files",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="use verbose logging",
    )

    parser.add_argument(
        "-J",
        "--show-json-schema",
        nargs=0,
        default=False,
        action=JsonSchemaAction,
        help="print the JSON schema and exit",
    )

    return parser


# -- run --------------------

def main(args=None):
    """Get JSON data from a URL and format a service status report.

    Parameters
    ----------
    args : `list` of `str`, optional
        The command-line arguments to parse,
        defaults to ``sys.argv[1:]``.

    Returns
    -------
    status : `int`
        The service status value, one of

        - 0: ``'OK'``
        - 1: ``'WARNING'``
        - 2: ``'CRITICAL'``
        - 3: ``'UNKNOWN'``
    """
    parser = create_parser()
    opts = parser.parse_args(args=args)

    # configure cache, logging, etc
    logfile = log_file(opts.log_dir, opts.url)
    logger = init_logging(
        name=PROG,
        level=logging.DEBUG if opts.verbose else logging.INFO,
        stream=logfile,
    )

    # configure cookiejar (use getattr becuase we use argparse.SUPPRESS)
    if not getattr(opts, "cookie_file", None):
        opts.cookie_file = default_cookie_file(opts.url)
    logger.debug(f"Using cookie jar from {opts.cookie_file}")

    # configure cache
    cache = cache_file(opts.cache_dir, opts.url)
    logger.debug(f"Will cache to: {cache}")

    status, message, detail = check_json(
        opts.url,
        cache=cache,
        logger=logger,
        timeout=opts.timeout,
        auth_type=opts.auth_type,
        idp=opts.identity_provider,
        cookiefile=opts.cookie_file,
        kerberos=opts.kerberos,
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

    # report plugin output in full HTML format
    print(message)
    if detail:
        print(detail)
    return status


# module execution
if __name__ == "__main__":
    sys.exit(main())
