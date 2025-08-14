
from unittest import mock

import pytest

from ...plugins import check_dqsegdb_latency


@mock.patch.object(check_dqsegdb_latency, "NOW", 1000000000)
@pytest.mark.parametrize(("mock_kw", "args", "status", "message"), [
    # OK, normal response
    pytest.param(
        {"json": {
            "known": [[999956800.0, 999999999.0]],
            "query_information": {
                "server_elapsed_query_time": "0.25",
            },
        }},
        [],
        0,
        "Latest known segment for X1:IMP-TEST_FLAG:0 is "
        "1 seconds old (999999999.0)",
        id="ok",
    ),
    # WARNING, high latency
    pytest.param(
        {"json": {
            "known": [[0, 999999000.0]],
            "query_information": {
                "server_elapsed_query_time": "0.25",
            },
        }},
        ["-w", "1000", "-c", "2000"],
        1,
        "Latest known segment for X1:IMP-TEST_FLAG:0 is "
        "1000 seconds old (999999000.0)",
        id="latency warning",
    ),
    # CRITICAL, high latency
    pytest.param(
        {"json": {
            "known": [[0, 999999000.0]],
            "query_information": {
                "server_elapsed_query_time": "0.25",
            },
        }},
        ["-w", "500", "-c", "1000"],
        2,
        "Latest known segment for X1:IMP-TEST_FLAG:0 is "
        "1000 seconds old (999999000.0)",
        id="latency critical",
    ),
    # CRITICAL: no segments
    pytest.param(
        {"json": {
            "known": [],
        }},
        [],
        2,
        "No segments in the last 43200s",
        id="no segments",
    ),
    # UNKNOWN: query failure
    pytest.param(
        {"status_code": 404, "reason": "Not Found"},
        [],
        3,
        "'404 Not Found' from https://segments.example.com",
        id="not found",
    ),
])
def test_check_dqsegdb_latency(
    capsys,
    requests_mock,
    mock_kw,
    args,
    status,
    message,
):
    # get start time of query from args
    end = 1000000000
    if "-c" in args:
        crit = float(args[args.index("-c") + 1])
        start = float(end - 2 * crit)
    else:
        start = end - 43200

    # mock the call
    requests_mock.get(
        "https://segments.example.com/dq/X1/IMP-TEST_FLAG/0"
        f"?s={start}&e={end}&include=known",
        **mock_kw,
    )

    # perform the check
    ret = check_dqsegdb_latency.main([
        "-H", "segments.example.com",
        "-f", "X1:IMP-TEST_FLAG:0",
        *args,
    ])

    # check that the plugin status is correct
    assert ret == status

    # check that the summary is correct
    stdout = capsys.readouterr().out
    assert stdout.startswith(message)

    # assert performance data in ok/warning responses
    if ret < 2:
        assert "'server_elapsed_query_time'=0.25s" in stdout
