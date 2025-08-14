# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Sphinx documentation utilities for igwn-monitoring-plugins."""

from pathlib import Path
from string import Template

try:
    from importlib.metadata import distribution
except ModuleNotFoundError:  # python < 3.8
    from importlib_metadata import distribution


SCRIPT_DOCS = Template("""
###################################
$prog
###################################

.. argparse::
   :module: $module
   :func: $func
   :prog: $prog
""".strip())


def _script_rst(entrypoint, func="create_parser"):
    return SCRIPT_DOCS.substitute(
        module=entrypoint.module,
        func=func,
        prog=entrypoint.name,
    )


def write_entrypoint_docs(
    outdir,
    dist="igwn_monitor",
    group="console_scripts",
    func="create_parser",
):
    """Generate an RST file for all entry points in the distribution.

    Parameters
    ----------
    outdir : `str`, `pathlib.Path`
        The directory in which to write the RST files

    dist : `str`
        The name of the distribution to scan.

    group : `str`
        The entry point group.

    func : `str`
        The name of the function that creates the `argparse.ArgumentParser`
        for the entry point.

    Returns
    -------
    paths : `list` of `pathlib.Path`
        The list of paths written.
    """
    paths = []
    Path(outdir).mkdir(exist_ok=True, parents=True)
    for ep in distribution(dist).entry_points:
        if group and ep.group != group:
            continue
        rst = outdir / f"{ep.name}.rst"
        content = _script_rst(ep, func=func)
        with open(rst, "w") as file:
            file.write(content)
        paths.append(rst)
    return paths
