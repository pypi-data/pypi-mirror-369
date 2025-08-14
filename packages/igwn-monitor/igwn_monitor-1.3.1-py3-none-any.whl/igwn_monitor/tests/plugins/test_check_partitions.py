
import subprocess
from unittest import mock

from ...plugins.check_partitions import main as check_partitions

SMLATENCY_OUTPUT = """
Partition GDS_Part latency, n=1  avg=6.54003  sig=0  max=6.54003
Partition GDS_Part latency, n=1  avg=6.43325  sig=0  max=6.43325
Partition GDS_Part latency, n=1  avg=6.52581  sig=0  max=6.52581
""".strip()


@mock.patch(  # smlatency
    "subprocess.run",
    side_effect=subprocess.TimeoutExpired(
        "cmd",
        10,
        output=SMLATENCY_OUTPUT.encode("utf-8"),
        stderr=None,
    ),
)
@mock.patch(  # smstat
    "subprocess.check_output",
    return_value="1234567890",
)
def test_check_partitions(mock1, mock2, capsys):
    ret = check_partitions([
        "-P", "GDS_Part",
    ])
    assert ret == 0
    stdout = capsys.readouterr().out
    message = "Latency OK: GDS_Part=6.54003s (1234567890.0)"
    assert stdout.startswith(message)


@mock.patch(  # smlatency
    "subprocess.run",
    side_effect=subprocess.CalledProcessError(
        1,
        "cmd",
        stderr="Unable to open partition: Test".encode("utf-8"),
    ),
)
def test_check_partitions_smlatency_fail(mock1, capsys):
    ret = check_partitions([
        "-P", "Test",
    ])
    assert ret == 2
    stdout = capsys.readouterr().out
    message = "Unable to open partition: Test"
    assert stdout.startswith(message)
