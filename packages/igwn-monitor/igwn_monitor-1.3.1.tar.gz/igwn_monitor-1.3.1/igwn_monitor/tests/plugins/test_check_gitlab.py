
import pytest

from ...plugins.check_gitlab import main as check_gitlab


@pytest.mark.parametrize(("mock_kw", "status", "message"), [
    # OK, normal response
    pytest.param(
        {"json": {
            "status": "ok",
            "master_check": [{"status": "ok"}],
            "db_check": [{"status": "ok"}],
        }},
        0,
        "Status: OK",
        id="ok",
    ),
    # WARNING: API reports an issue
    pytest.param(
        {"json": {
            "status": "failed",
            "master_check": [{"status": "failed"}],
        }},
        1,
        "Status: FAILED",
        id="failure",
    ),
    # WARNING: failed to parse API response
    pytest.param(
        {"text": "Text response"},
        1,
        "Failed to parse JSON from API query",
        id="invalid response",
    ),
    # CRITICAL: failed to talk to gitlab
    pytest.param(
        {"status_code": 403, "reason": "Forbidden"},
        2,
        "403 Client Error: Forbidden",
        id="request exception",
    ),
])
def test_check_gitlab(capsys, requests_mock, mock_kw, status, message):
    requests_mock.get(
        "https://git.example.com/-/readiness?all=1",
        **mock_kw,
    )
    ret = check_gitlab([
        "-H", "git.example.com",
    ])
    assert ret == status
    captured = capsys.readouterr()
    assert captured.out.startswith(message)
