# Copyright (c) 2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Test for the `check_pelican_latency` plugin."""

import json
import subprocess
from unittest import mock

import pytest

from ...plugins import (
    check_file_latency,
    check_pelican_latency,
)
from ...utils import NagiosStatus


def mock_to_gps(arg):
    """Mock getting GPS time 'now' for tests."""
    if arg == "now":
        return 500
    return check_file_latency.to_gps(arg)


@pytest.fixture
def mock_run_pelican():
    """Mock `run_pelican`."""
    with mock.patch(
        #"igwn_monitor.plugins.check_pelican_latency.run_pelican",
        "subprocess.run",
    ) as mocker:
        mocker.side_effect = [
            subprocess.CompletedProcess(
                ["pelican", "object", "ls", "thing"],
                0,
                json.dumps(out),
                "",
            ) for out in [
                ["test-1", "test-2"],
                ["X-TEST-100-50.gwf", "X-TEST-150-50.gwf"],
                ["X-TEST-200-50.gwf", "X-TEST-250-50.gwf"],
            ]
        ]
        yield mocker


@pytest.mark.parametrize(("args", "status", "message"), [
    pytest.param(
        (),
        0,
        "Latest file (X-TEST-250-50.gwf) is 200 seconds old",
        id="OK",
    ),
    pytest.param(
        ("--ordered-dirs",),  # only runs the first two calls
        0,
        "Latest file (X-TEST-150-50.gwf) is 300 seconds old",
        id="OK",
    ),
    pytest.param(
        ("-w", 50),
        1,
        "Latest file (X-TEST-250-50.gwf) is 200 seconds old",
        id="WARNING",
    ),
    pytest.param(
        ("-w", 50, "-c", 100),
        2,
        "Latest file (X-TEST-250-50.gwf) is 200 seconds old",
        id="CRITICAL",
    ),
])
@pytest.mark.usefixtures("mock_run_pelican")
@mock.patch("igwn_monitor.plugins.check_file_latency.to_gps", mock_to_gps)
def test_check_pelican_latency(
    capsys,
    args,
    status,
    message,
):
    """Test `check_pelican_latency` latency checking."""
    # perform the check
    ret = check_pelican_latency.main([
        "-g", "/igwn/test-*/X-TEST-*.gwf",
        *map(str, args),
    ])

    # check that the plugin status is correct
    assert ret == status

    # check that the summary is correct
    stdout = capsys.readouterr().out
    assert stdout.startswith(message)


def test_check_pelican_latency_unknown_error(
    capsys,
    mock_run_pelican,
):
    """Test that `check_pelican_latency` reports UNKNOWN when pelican fails."""
    mock_run_pelican.side_effect = subprocess.CalledProcessError(
        1,
        "pelican object ls",
    )
    ret = check_pelican_latency.main([
        "-g", "/igwn/test-*/X-TEST-*.gwf",
    ])
    assert ret == NagiosStatus.UNKNOWN
    stdout = capsys.readouterr().out
    assert stdout.startswith("Pelican query failed\nCommand 'pelican object ls")


def test_check_pelican_latency_unknown_empty(
    capsys,
    mock_run_pelican,
):
    """Test that `check_pelican_latency` reports UNKNOWN when no files are found."""
    mock_run_pelican.side_effect = [subprocess.CompletedProcess([], 0, "[]", "")]
    ret = check_pelican_latency.main([
        "-g", "/igwn/test-*/X-TEST-*.gwf",
    ])
    assert ret == NagiosStatus.UNKNOWN
    stdout = capsys.readouterr().out
    assert stdout.startswith("No files found for query")
