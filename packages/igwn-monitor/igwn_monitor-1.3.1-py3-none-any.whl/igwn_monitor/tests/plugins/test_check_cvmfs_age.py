
import json
import time
from unittest import mock

import pytest

from ...plugins import check_cvmfs_age
from ...plugins.check_json import (
    SCHEMA as JSON_SCHEMA,
    validate_json,
)

CVMFSPUBLISHED = """
CXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
B123456
RXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
D123
S1234
Gyes
Ano
Nrepo.cvmfs.example.com
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
HXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
T1000000000
MXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
YXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
--
binary data
""".strip()


@mock.patch.object(check_cvmfs_age, "NOW", 1000001000)
@pytest.mark.parametrize(("repo", "mock_kw", "args", "status", "message"), [
    # OK, normal response
    pytest.param(
        "repo.cvmfs.example.com",
        {"text": CVMFSPUBLISHED},
        (),
        0,
        "/cvmfs/repo.cvmfs.example.com was last published 1000s ago",
        id="ok",
    ),
    # high latency WARNING
    pytest.param(
        "repo.cvmfs.example.com",
        {"text": CVMFSPUBLISHED},
        ("-w", "500", "-c", "2000"),
        1,
        "/cvmfs/repo.cvmfs.example.com was last published 1000s ago",
        id="warning",
    ),
    # high latency CRITICAL
    pytest.param(
        "repo.cvmfs.example.com",
        {"text": CVMFSPUBLISHED},
        ("-w", "500", "-c", "800"),
        2,
        "/cvmfs/repo.cvmfs.example.com was last published 1000s ago",
        id="critical",
    ),


    # wrong repo in cvmfspublished
    pytest.param(
        "other.cvmfs.example.com",
        {"text": CVMFSPUBLISHED},
        (),
        3,
        "Repository name 'other.cvmfs.example.com' doesn't match "
        ".cvmfspublished manifest ('repo.cvmfs.example.com')",
        id="wrong repo",
    ),
    # bad content
    pytest.param(
        "other.cvmfs.example.com",
        {"text": ""},
        (),
        3,
        "Failed to parse .cvmfspublished",
        id="empty",
    ),
    # bad response
    pytest.param(
        "other.cvmfs.example.com",
        {"status_code": 404, "reason": "Not Found"},
        (),
        3,
        "404 Client Error: Not Found for url: ",
        id="404",
    ),
])
def test_check_cvmfs_age(
    capsys,
    requests_mock,
    repo,
    mock_kw,
    args,
    status,
    message,
):
    # mock the call
    requests_mock.get(
        f"http://cvmfs.example.com:8000/cvmfs/{repo}/.cvmfspublished",
        **mock_kw,
    )

    # perform the check
    ret = check_cvmfs_age.main([
        "-H", "cvmfs.example.com",
        "--repository", repo,
        *args,
    ])

    # check that the plugin status is correct
    assert ret == status

    # check that the summary is correct
    stdout = capsys.readouterr().out
    assert stdout.startswith(message)


@mock.patch.object(check_cvmfs_age, "NOW", 1000001000)
def test_check_cvmfs_age_json(requests_mock, tmp_path):
    # mock the call
    requests_mock.get(
        "http://cvmfs.example.com:8000"
        "/cvmfs/repo.cvmfs.example.com/.cvmfspublished",
        text=CVMFSPUBLISHED,
    )

    outfile = tmp_path / "status.json"

    # perform the check with JSON output
    ret = check_cvmfs_age.main([
        "-H", "cvmfs.example.com",
        "--repository", "repo.cvmfs.example.com",
        "--output-file", str(outfile),
        "--output-json-expiry", "1000",
    ])
    data = json.loads(outfile.read_text())
    assert ret == 0

    # check JSON data
    data = json.loads(outfile.read_text())
    validate_json(instance=data, schema=JSON_SCHEMA)
    assert abs(data["created_unix"] - time.time()) < 100
    assert data["status_intervals"] == [
        {
            "start_sec": 0,
            "end_sec": 1000,
            "num_status": 0,
            "txt_status": (
                "/cvmfs/repo.cvmfs.example.com was last published "
                "1000s ago | 'age'=1000s;;;0"
            ),
        },
        {
            "start_sec": 1000,
            "num_status": 3,
            "txt_status": "check_cvmfs_age is not updating",
        },
    ]
