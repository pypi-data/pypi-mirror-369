
import os

import pytest

from ...plugins.check_gwosc import main as check_gwosc


@pytest.mark.parametrize(("mock_kw", "status", "message"), [
    # OK, normal response
    pytest.param(
        {"json": {
            "GWTC-3-confident": 0,
            "TEST": 1,
        }},
        0,
        "GWOSC server seems OK",
        id="ok",
    ),
    # WARNING: API reports an issue
    pytest.param(
        {"json": {}},
        1,
        "GWTC-3-confident not in list of releases",
        id="failure",
    ),
    # WARNING: failed to parse API response
    pytest.param(
        {"text": "Text response"},
        1,
        "Failed to parse JSON from API query",
        id="invalid response",
    ),
    # CRITICAL: failed to talk to server
    pytest.param(
        {"status_code": 403, "reason": "Forbidden"},
        2,
        "403 Client Error: Forbidden",
        id="request exception",
    ),
])
def test_check_gwosc(capsys, requests_mock, mock_kw, status, message):
    # mock the call
    requests_mock.get(
        "https://gwosc.example.com/eventapi/json/",
        **mock_kw,
    )

    # perform the check
    ret = check_gwosc([
        "-H", "gwosc.example.com",
    ])

    # check that the plugin status is correct
    assert ret == status

    # check that the summary is correct
    stdout = capsys.readouterr().out
    assert stdout.startswith(message)

    # assert detail is well formatted
    if ret == 0:
        assert f"Datasets:{os.linesep}  GWTC-3-confident" in stdout
