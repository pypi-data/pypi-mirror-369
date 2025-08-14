# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Tests for :mod:`igwn_monitor.auth`."""

from .. import auth


def test_write_krb5_config(tmp_path):
    """Test that :func:`igwn_monitor.auth.write_krb5_config` works."""
    path = auth.write_krb5_config(
        tmp_path / "krb5.conf",
        "kdc.example.com",
        "EXAMPLE.COM",
        str(tmp_path / "ccache"),
    )
    conf = path.read_text()
    assert "default_realm = EXAMPLE.COM" in conf
    assert f"default_ccache_name = {tmp_path / 'ccache'}" in conf
