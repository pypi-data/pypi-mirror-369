# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Tests for :mod:`igwn_monitor.plugins`."""

import pytest

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # python < 3.8
    importlib_metadata = pytest.importorskip("importlib_metadata")

from .. import (
    __name__,
    __version__,
)

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

# discover all of the registered console_scripts for this project
try:
    ENTRY_POINTS = importlib_metadata.distribution(__name__).entry_points
except importlib_metadata.PackageNotFoundError:  # package not built/installed
    ENTRY_POINTS = []
SCRIPTS = [ep for ep in ENTRY_POINTS if ep.group == "console_scripts"]
PARAMETRIZE_SCRIPTS = pytest.mark.parametrize(
    "script",
    [pytest.param(ep, id=ep.name) for ep in SCRIPTS],
)


def _run_entry_point(script, args):
    main = script.load()
    with pytest.raises(SystemExit):
        main(args)


@PARAMETRIZE_SCRIPTS
def test_help(script):
    return _run_entry_point(script, ["--help"])


@PARAMETRIZE_SCRIPTS
def test_version(capsys, script):
    _run_entry_point(script, ["--version"])
    out, err = capsys.readouterr()
    assert out.strip() == f"{script.name} {__version__}"
