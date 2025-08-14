# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

from pathlib import Path

from igwn_monitor import __version__ as release
from igwn_monitor.sphinx import write_entrypoint_docs

# -- metadata

project = "igwn-monitoring-plugins"
copyright = "2023-2025 Cardiff University"
author = "Duncan Macleod"
version = release.split(".dev", 1)[0]

# -- sphinx config

needs_sphinx = "4.0"
extensions = [
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_automodapi.automodapi",
    "sphinxarg.ext",
    "sphinx-jsonschema",
]
default_role = "obj"
exclude_patterns = [
    "references.rst",
]

# epilog
rst_epilog = "\n.. include:: /references.rst"

# -- theme options

html_theme = "sphinx_rtd_theme"
pygments_style = "monokai"

# -- extensions

intersphinx_mapping = {
    "ldap3": ("https://ldap3.readthedocs.io/en/latest/", None),
    "python": ("https://docs.python.org/", None),
    "requests": ("https://requests.readthedocs.io/en/stable/", None),
}

autosummary_generate = True
autoclass_content = "class"


# -- run

def write_plugins_sources(app):
    pluginsdir = Path(app.srcdir) / "plugins"
    write_entrypoint_docs(
        pluginsdir,
        dist="igwn-monitor",
        func="create_parser",
    )


def setup(app):
    app.connect("builder-inited", write_plugins_sources)
