
"""Tests for the `check_command` plugin."""

import re
import sys
from os.path import basename

import pytest

from ...plugins import check_command

EXE = sys.executable
EXE_NAME = basename(EXE)


@pytest.mark.parametrize(("args", "status", "message"), [
    # OK
    pytest.param(
        (
            "--verbose", "--empty-env",
            EXE, "--version",
        ),
        0,
        f"{EXE_NAME} succeeded .*Python 3",
        id="ok",
    ),
    # fail
    pytest.param(
        (
            EXE, "-c", "import sys; sys.exit(10)",
        ),
        2,
        rf"{EXE_NAME} failed \(exited with code 10\)",
        id="fail",
    ),
    # fail as warning
    pytest.param(
        (
            "--warning-code", "10",
            EXE, "-c", "import sys; sys.exit(10)",
        ),
        1,
        rf"{EXE_NAME} failed \(exited with code 10\)",
        id="warning",
    ),
    # timeout
    pytest.param(
        (
            "--timeout", "1",
            EXE, "-c", "import time; time.sleep(10)",
        ),
        2,
        rf"{EXE_NAME} timed out",
        id="timeout",
    ),
    # timeout unknown
    pytest.param(
        (
            "--timeout", "1", "--timeout-unknown",
            EXE, "-c", "import time; time.sleep(10)",
        ),
        3,
        rf"{EXE_NAME} timed out",
        id="timeout unknown",
    ),
    # executable not found
    pytest.param(
        (
            "--verbose",
            "badbadbad",
        ),
        3,
        "Failed to run badbadbad .* No such file or directory: 'badbadbad'",
        id="filenotfound",
    )
])
def test_check_command(capsys, args, status, message):
    """Check that `check_command` works."""
    # run the check
    ret = check_command.main(args)
    assert ret == status

    # ensure that the most recent file is found
    stdout = capsys.readouterr().out
    assert re.match(message, stdout, re.DOTALL)
