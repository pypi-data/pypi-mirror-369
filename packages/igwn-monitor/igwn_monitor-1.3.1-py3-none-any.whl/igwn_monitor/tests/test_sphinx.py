# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Tests for :mod:`igwn_monitor.sphinx`."""

import sys
from unittest import mock

try:
    from importlib.metadata import EntryPoint
except ModuleNotFoundError:  # python < 3.8
    from importlib_metadata import EntryPoint

import pytest

from .. import sphinx as imp_sphinx


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="write_entrypoint_docs only supported for Python >= 3.9",
)
@mock.patch("igwn_monitor.sphinx.distribution")
def test_write_entrypoint_docs(mocked, tmp_path):
    """Test that `igwn_monitor.sphinx.write_entrypoint_docs` generates an RST
    file with the necessary content.
    """
    # mock the entry point list
    mocked.return_value.entry_points = [EntryPoint(
        name="test",
        group="console_scripts",
        value="test_package.test_module:main",
    )]

    # run the function
    paths = imp_sphinx.write_entrypoint_docs(
        tmp_path,
    )

    # check the output
    assert len(paths) == 1
    assert paths[0] == tmp_path / "test.rst"
    content = paths[0].read_text()
    assert ":module: test_package.test_module" in content
    assert ":func: create_parser" in content
    assert ":prog: test" in content
