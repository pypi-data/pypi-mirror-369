# -*- python -*-

import json

import pytest
from freezegun import freeze_time

from ...plugins import check_json

EXAMPLE_JSON = {
    "created_unix": 1704067200,  # 2024-01-01
    "status_intervals": [
        {
            "start_sec": 0,
            "num_status": 0,
            "txt_status": "Test check is OK|'response_time'=1.23s;;;0;",
            "end_sec": 3600,
        },
        {
            "start_sec": 3600,
            "num_status": 3,
            "txt_status": "Test check is not updating",
        },
    ],
    "author": "Test <test@example.com>",
    "random key": "random value",
    "ok_status": "This is what OK means",
}


@pytest.fixture
def json_file(tmp_path):
    path = tmp_path / "test.json"
    with open(path, "w") as file:
        json.dump(EXAMPLE_JSON, file)
    return path


# -- unit tests

def test_get_json_file(json_file):
    raw, data = check_json._get_json_file(f"file://{json_file}")
    assert data == EXAMPLE_JSON


# -- end-to-end tests

@pytest.mark.parametrize(("data", "time", "result", "message"), [
    pytest.param(
        EXAMPLE_JSON,
        "2024-01-01 00:00:01",
        EXAMPLE_JSON["status_intervals"][0]["num_status"],
        EXAMPLE_JSON["status_intervals"][0]["txt_status"],
        id="OK",
    ),
    pytest.param(
        # remove optional key
        {k: v for k, v in EXAMPLE_JSON.items() if k != "ok_status"},
        "2024-01-01 00:00:01",
        EXAMPLE_JSON["status_intervals"][0]["num_status"],
        EXAMPLE_JSON["status_intervals"][0]["txt_status"],
        id="OK 2",
    ),
    pytest.param(
        EXAMPLE_JSON,
        "2024-01-02 00:00:00",
        EXAMPLE_JSON["status_intervals"][1]["num_status"],
        EXAMPLE_JSON["status_intervals"][1]["txt_status"],
        id="expired",
    ),
    pytest.param(
        EXAMPLE_JSON,
        "2023-01-01 00:00:00",
        3,
        "No status_interval matches elapsed time",
        id="clock skew",
    ),
    pytest.param(
        {},
        "2024-01-01 00:00:00",
        3,
        "JSON failed validation against the schema",
        id="empty",
    ),
])
def test_check_json(
    capsys,
    requests_mock,
    tmp_path,
    data,
    time,
    result,
    message,
):
    # mock the request
    requests_mock.get(
        "http://example.com/remote.json",
        json=data,
    )

    # perform the check (frozen in time)
    with freeze_time(time):
        ret = check_json.main([
            "--url", "http://example.com/remote.json",
            "--log-dir", str(tmp_path),
            "--verbose",
        ])

    # check that the plugin status is correct
    assert ret == result

    # check that the summary is correct
    stdout = capsys.readouterr().out
    assert message in stdout  # wrapped in HTML


def test_check_json_schema(capsys, tmp_path):
    with pytest.raises(SystemExit, match="0"):
        check_json.main([
            "--show-json-schema",
            "--log-dir", str(tmp_path),
        ])
    stdout = capsys.readouterr().out
    schema = json.loads(stdout)
    assert schema == check_json.SCHEMA
