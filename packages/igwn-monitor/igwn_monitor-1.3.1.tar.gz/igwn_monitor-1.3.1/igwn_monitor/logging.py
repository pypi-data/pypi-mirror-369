# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Logging utilities IGWN Monitors."""

import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

try:
    from coloredlogs import (
        ColoredFormatter,
        terminal_supports_colors,
    )
except ImportError:
    def terminal_supports_colors(stream):  # cannot use colours
        return False

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"


def init_logging(name, level=logging.INFO, stream=sys.stderr):
    """Return the logger with the given name, or create one as needed.

    If the logger as no handlers attached already, a new
    `logging.Handler` will be created and attached based on ``stream``.

    Parameters
    ----------
    name : `str`
        The name of the logger.

    level : `int`, `str`
        The level to set on the logger.

    stream : `io.IOBase`, `str`
        The stream to write log messages to.
        If a `str` is given as either ``"stdout"``, ``"stderr"`` logs
        will be written to those default streams, any other `str` is
        interpreted as a file path in which to maintain a
        `logging.TimedRotatingFileHandler` with daily rotation and
        three days of backup.

    Returns
    -------
    logger : `logging.Logger`
        A new, or existing, `Logger` instance, with at least one
        `~logging.Handler` attached.
    """
    # stream to console
    if stream in ("stdout", "stderr"):
        stream = getattr(sys, stream)

    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level)
    if not logger.handlers:
        if isinstance(stream, (str, Path)):
            # create the parent directory
            Path(stream).parent.mkdir(parents=True, exist_ok=True)
            # create the rotating file handler
            handler = TimedRotatingFileHandler(
                str(stream),
                when="d",
                interval=1,
                backupCount=3,
            )
            # if logging to file, never use colour
            formatter_class = logging.Formatter
        else:
            handler = logging.StreamHandler(stream)
            if terminal_supports_colors(stream):
                formatter_class = ColoredFormatter
            else:
                formatter_class = logging.Formatter
        handler.setFormatter(formatter_class(
            "%(asctime)s | %(name)s | %(levelname)+8s | %(message)s",
        ))
        logger.addHandler(handler)
    return logger
