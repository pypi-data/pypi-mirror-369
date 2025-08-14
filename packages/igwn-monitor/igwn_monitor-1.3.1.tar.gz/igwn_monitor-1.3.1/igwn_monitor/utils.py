# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Utilities for IGWN monitoring."""

from enum import IntEnum

from gpstime import gpstime

from .compat import UTC


class NagiosStatus(IntEnum):
    """Nagios exit codes and status strings."""
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3


def _format_metric_value(value, unit=None):
    if isinstance(value, (list, tuple)):
        out = ""
        for val in value:
            out += ";" + _format_metric_value(val, unit=unit)
            unit = None
        return out.lstrip(";")
    if value is None:
        return ""
    return str(value) + str(unit or "")


def format_performance_metrics(metrics, unit=None):
    """Format a dict of performance metrics.

    See https://icinga.com/docs/icinga-2/latest/doc/05-service-monitoring/#performance-data-metrics.

    The metrics should be a `dict` of label, value pairs, where the value
    can be either a `str`, which is formatted verbatim, or a sequence
    (e.g. `tuple`) where the values are formatted ';'-delimited.

    Examples
    --------
    >>> format_performance_metrics({"label": "value"})
    "'label'=value"
    >>> format_performance_metrics({"time": 1.23}, unit="s")
    "'time'=1.23s"
    >>> format_performance_metrics({"label": "value", "label2": ('10s', '15', '20')})
    "'label'=value 'label2'=10s;15;20"
    """
    formatted = []
    for label, value in metrics.items():
        formatted.append(f"'{label}'={_format_metric_value(value, unit=unit)}")
    return " ".join(formatted)


# -- GPS conversion -------------------

def from_gps(gps):
    """Convert a GPS time into a `gpstime.gpstime`.

    Parameters
    ----------
    gps : `float`, `int`
        The GPS timestamp to convert.

    Returns
    -------
    dt : `gpstime.gpstime`
        The UTC-localised `gpstime.gpstime` represented by the input GPS.

    Examples
    --------
    >>> from_gps(0)
    gpstime(1980, 1, 6, 0, 0, tzinfo=datetime.timezone.utc)
    >>> from_gps(1000000000)
    gpstime(2011, 9, 14, 1, 46, 25, tzinfo=datetime.timezone.utc)
    """
    return gpstime.fromgps(gps).astimezone(UTC)


def to_gps(dt):
    """Convert a timestamp or `datetime.datetime` into a GPS time.

    Parameters
    ----------
    dt : `str`, `float`, `int`, `datetime.datetime`
        A datetime string, Unix epoch, or datetime to convert to GPS.

    Returns
    -------
    gps : `float`
        The GPS time represented by the input datetime.

    Examples
    --------
    >>> to_gps(datetime(2024, 1, 1))
    1388102418.0
    """
    if isinstance(dt, str):
        return gpstime.parse(dt).gps()
    if isinstance(dt, (int, float)):  # timestamp
        return gpstime.fromtimestamp(dt).gps()
    return gpstime.fromdatetime(dt).gps()
