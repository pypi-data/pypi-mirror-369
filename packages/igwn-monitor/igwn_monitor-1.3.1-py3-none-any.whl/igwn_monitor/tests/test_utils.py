# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Tests for :mod:`igwn_monitor.utils`."""

from datetime import (
    datetime,
    timezone,
)
from unittest import mock

import pytest

from .. import utils as imp_utils


@pytest.mark.parametrize(("args", "result"), [
    # simple key value
    (
        ({"label": "value"},),
        "'label'=value",
    ),
    # value and thresholds with separate unit spec
    (
        ({"time": (1.23, 5, 10)}, "s"),
        "'time'=1.23s;5;10",
    ),
    # multiple key/value pairs
    (
        ({"label": "value", "label2": ("10s", "15", "20")},),
        "'label'=value 'label2'=10s;15;20",
    )
])
def test_format_performance_metrics(args, result):
    assert imp_utils.format_performance_metrics(*args) == result


@pytest.mark.parametrize(("in_", "out"), [
    (0, datetime(1980, 1, 6, tzinfo=timezone.utc)),
    (1000000000, datetime(2011, 9, 14, 1, 46, 25, tzinfo=timezone.utc)),
])
def test_from_gps(in_, out):
    assert imp_utils.from_gps(in_) == out


@mock.patch(  # mock 'now' to be Jan 1 2024
    "igwn_monitor.utils.gpstime.now",
    lambda: imp_utils.gpstime(2024, 1, 1),
)
@pytest.mark.parametrize(("in_", "out"), [
    (datetime(1980, 1, 6, tzinfo=timezone.utc), 0.0),
    (datetime(2011, 9, 14, 1, 46, 25, tzinfo=timezone.utc), 1000000000.0),
    (315964800, 0.),
    (315964801.0, 1.),
    ("now", 1388102418.0),  # <-- see mock above
])
def test_to_gps(in_, out):
    assert imp_utils.to_gps(in_) == out
