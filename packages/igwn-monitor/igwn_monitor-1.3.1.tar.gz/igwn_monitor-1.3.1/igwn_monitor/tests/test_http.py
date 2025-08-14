# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Tests for :mod:`igwn_monitor.http`."""

import pytest

from .. import http


@pytest.mark.parametrize(("args", "kwargs", "result"), [
    # just a host name
    (
        ("example.com",),
        {},
        "https://example.com/",
    ),
    # host specifies scheme
    (
        ("http://example.com",),
        {},
        "http://example.com/",
    ),
    # host including port
    (
        ("example.com:80",),
        {},
        "http://example.com:80/",
    ),
    (
        ("example.com:8000",),
        {},
        "http://example.com:8000/",
    ),
    (
        ("example.com:8443",),
        {},
        "https://example.com:8443/",
    ),
    # paths (with extra leading slashes)
    (
        ("example.com", "/path", "/path2"),
        {},
        "https://example.com/path/path2",
    ),
    # host including path with trailing slash
    (
        ("example.com/path", "path2/"),
        {},
        "https://example.com/path/path2/",
    ),
    # host including port and path
    (
        ("example.com:80/path", "path2"),
        {},
        "http://example.com:80/path/path2",
    ),
    # host including port and path but duplicate port keyword
    (
        ("example.com:80/path", "path2"),
        {"port": 1234},
        "http://example.com:80/path/path2",
    ),
    # kwargs
    (
        ("example.com", "path", "path2"),
        {
            "scheme": "imap",
            "port": 1234,
            "query": "a=1",
            "fragment": "loc",
        },
        "imap://example.com:1234/path/path2?a=1#loc",
    ),
    (
        ("example.com", "path", "path2"),
        {
            "scheme": "imap",
            "port": 1234,
            "query": {"key": "value", "key2": 0},
            "fragment": "loc",
        },
        "imap://example.com:1234/path/path2?key=value&key2=0#loc",
    ),

])
def test_make_url(args, kwargs, result):
    assert http.make_url(*args, **kwargs) == result


class TestIgwnOmniAuth:
    IgwnOmniAuth = http.IgwnOmniAuth

    def test_init(self):
        auth = self.IgwnOmniAuth(
            idp="https://idp.example.com",
            kerberos=False,
            token="testtoken",
        )
        assert auth.kerberos is False
        assert auth.token == "testtoken"
        assert auth.idp == "https://idp.example.com"
