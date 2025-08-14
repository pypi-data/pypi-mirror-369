
"""Tests for the `check_file_latency` plugin."""

from time import sleep

import pytest

from ...plugins import check_file_latency


@pytest.mark.parametrize(("args", "status"), [
    pytest.param([], 0, id="no thresholds"),
    pytest.param(["-w", "100", "-c", "200"], 0, id="below threshold"),
    pytest.param(["-w", "10", "-c", "100"], 1, id="warning"),
    pytest.param(["-w", "10", "-c", "20"], 2, id="critical"),
])
def test_check_file_latency(tmp_path, capsys, args, status):
    """Check that `check_file_latency` works with thresholds."""
    (tmp_path / "X-TEST-0-10.gwf").touch()
    (tmp_path / "X-TEST-10-10.gwf").touch()
    (tmp_path / "X-TEST-20-10.gwf").touch()
    (tmp_path / "Y-TEST-10-10.gwf").touch()

    # run the check
    ret = check_file_latency.main([
        "-p", str(tmp_path),
        "-n", "100",
        *args,
    ])
    assert ret == status

    # ensure that the most recent file is found
    stdout = capsys.readouterr().out
    assert stdout.startswith(
        "Latest file (X-TEST-20-10.gwf) is 70 seconds old",
    )


def test_check_file_latency_ctime(tmp_path, capsys):
    """Check that specifying ``--scheme ctime`` works."""
    (tmp_path / "X-TEST-10-10.gwf").touch()
    sleep(.1)
    (tmp_path / "X-TEST-0-10.gwf").touch()

    # run the check
    ret = check_file_latency.main([
        "-p", str(tmp_path),
        "-s", "ctime",
    ])
    assert ret == 0

    # ensure that the most recent file is found
    stdout = capsys.readouterr().out
    assert stdout.startswith(
        "Latest file (X-TEST-0-10.gwf) is ",
    )


def test_check_file_latency_file(tmp_path, capsys):
    """Check that `check_file_latency` works with filenames."""
    path = tmp_path / "test.txt"
    path.touch()
    sleep(.1)

    # run the check
    ret = check_file_latency.main([
        "-p", str(path),
        "-s", "ctime",
    ])
    assert ret == 0

    # ensure that the most recent file is found
    stdout = capsys.readouterr().out
    assert stdout.startswith(
        f"Latest file ({path.name}) is ",
    )


def test_check_file_latency_disable_find():
    """Check that the `disable_find` option works."""
    # run the check
    status, message = check_file_latency.check_file_latency(
        "A-TEST-0-1.gwf",
        now=10,
        disable_find=True,
    )
    assert status == 0
    assert message.startswith(
        "Latest file (A-TEST-0-1.gwf) is 9 seconds old",
    )


def test_check_file_latency_empty(tmp_path):
    """Check that an empty directory results in UNKNOWN."""
    # run the check
    status, message = check_file_latency.check_file_latency(
        str(tmp_path),
    )
    assert status == 3
    assert message == f"No files found matching '{tmp_path}'"
