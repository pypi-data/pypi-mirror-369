# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

"""Custom logging functionality helpers."""

import logging
from typing import ClassVar


class ColourFormatter(logging.Formatter):
    """A coloured log formatter meant for stdout.

    References:
        Stack Overflow: https://stackoverflow.com/a/56944256
    """

    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    formatting = "[{asctime}] - [{levelname:>9s} ] - {message}"

    FORMATS: ClassVar[dict[int, str]] = {
        logging.DEBUG: formatting,
        logging.INFO: formatting,
        logging.WARNING: yellow + formatting + reset,
        logging.ERROR: red + formatting + reset,
        logging.CRITICAL: bold_red + formatting + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Formats the given record as a string.

        Args:
            record (logging.LogRecord): Record to format.

        Returns:
            The record formatter as a string.
        """
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(
            log_format, style="{", datefmt="%Y-%m-%d %H:%M:%S"
        )
        return formatter.format(record)
