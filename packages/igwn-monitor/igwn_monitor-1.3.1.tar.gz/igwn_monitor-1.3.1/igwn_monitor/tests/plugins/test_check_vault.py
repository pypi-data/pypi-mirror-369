
import pytest
import requests

from ...plugins.check_vault import main as check_vault


@pytest.mark.parametrize(("mock_kw", "status", "message"), [
    # OK, normal response
    pytest.param(
        {"json": {
            "initialized": True,
            "sealed": False,
            "standby": False,
        }},
        0,
        "Vault ready",
        id="ok",
    ),
    # WARNING: standby
    pytest.param(
        {
            "json": {
                "initialized": True,
                "sealed": False,
                "standby": True,
            },
            "status_code": 429,
        },
        1,
        "Vault in standby",
        id="standby",
    ),
    # CRITICAL: sealed
    pytest.param(
        {
            "json": {
                "initialized": True,
                "sealed": True,
                "standby": False,
            },
            "status_code": 503,
        },
        2,
        "Vault sealed",
        id="sealed",
    ),
    # CRITICAL: 404
    pytest.param(
        {
            "json": {
                "errors": [],
            },
            "status_code": 404,
            "reason": "Not Found",
        },
        2,
        "404 Client Error: Not Found for url: https://vault.example.com",
        id="not found",
    ),
    # UNKNOWN: new response
    pytest.param(
        {
            "json": {
                "errors": [],
            },
            "status_code": 204,
        },
        3,
        "Unknown status (204)",
        id="unknown",
    ),

    # WARNING: failed to parse API response
    pytest.param(
        {"text": "Text response"},
        1,
        "Failed to parse JSON from API query",
        id="invalid response",
    ),
    # CRITICAL: failed to talk to vault
    pytest.param(
        {"exc": requests.exceptions.ConnectionError("message")},
        2,
        "message",
        id="request exception",
    ),
])
def test_check_vault(capsys, requests_mock, mock_kw, status, message):
    requests_mock.get(
        "https://vault.example.com:8200/v1/sys/health",
        **mock_kw,
    )
    ret = check_vault([
        "-H", "vault.example.com",
    ])
    assert ret == status
    stdout = capsys.readouterr().out
    print(message)
    print(stdout)
    assert stdout.startswith(message)
