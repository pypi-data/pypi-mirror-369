# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Compatibility shims for old Python."""

try:
    from contextlib import nullcontext
except ImportError:  # python < 3.7
    from contextlib import contextmanager

    @contextmanager
    def nullcontext(enter_result=None):
        yield enter_result

try:
    from shlex import join as shlex_join
except ImportError:  # python < 3.8
    import shlex

    def shlex_join(split):
        """Backport of `shlex.join` from Python 3.8."""
        return " ".join(map(shlex.quote, split))

try:
    from datetime import UTC
except ImportError:  # python < 3.11
    from datetime import timezone
    UTC = timezone.utc
