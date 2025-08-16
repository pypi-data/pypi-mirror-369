# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

import logging
import sys

import click

from drim2p import convert
from drim2p import deltaf
from drim2p import draw
from drim2p import extract
from drim2p import logs
from drim2p import motion

_logger = logging.getLogger("drim2p")


class LoggingVerbosity:
    """Verbosity level of the package logging."""

    ERROR = -2
    WARNING = -1
    INFO = 0
    DEBUG = 1


@click.group(invoke_without_command=True)
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    required=False,
    count=True,
    help="Set verbosity level. Level 0 is INFO (default). Level 1 is DEBUG.",
)
@click.option(
    "-q",
    "--quiet",
    "quietness",
    required=False,
    count=True,
    help=(
        "Suppress log output. One '--quiet' suppresses INFO messages. Two '--quiet' "
        "and up suppresses WARNING messages."
        "This overrides verbosity set using '--verbose'."
    ),
)
@click.option(
    "--no-colour",
    required=False,
    is_flag=True,
    help="Disable logging colours.",
)
def drim2p(verbosity: int = 0, quietness: int = 0, no_colour: bool = False) -> None:
    """A dreamy 2-photon imaging processing pipeline.
    \f

    Args:
        verbosity (int, optional):
            Verbosity level. Level 0 is INFO (default). Level 1 is DEBUG.
        quietness (int, optional):
            Quietness level. Level 0 suppresses INFO messages. Level 1 suppresses
            WARNING messages.
        no_colour (bool, optional): Whether to disable logging colours.
    """  # noqa: D205, D301, D415
    set_up_logging(verbosity, quietness, no_colour)


def set_up_logging(verbosity: int, quietness: int, no_colour: bool) -> None:
    """Sets the logging level package.

    Args:
        verbosity (int):
            Verbosity level. Level 0 is INFO (default). Level 1 is DEBUG.
        quietness (int):
            Quietness level. Level 0 suppresses INFO messages. Level 1 suppresses
            WARNING messages.
        no_colour (bool): Whether to disable logging colours.
    """
    if no_colour:
        formatter = logging.Formatter(
            "[{asctime}] - [{levelname:>9s} ] - {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = logs.ColourFormatter()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    _logger.addHandler(console_handler)

    # Quietness overrides verbosity
    level = -quietness if quietness > 0 else verbosity
    if level <= LoggingVerbosity.ERROR:
        _logger.setLevel(logging.ERROR)
    elif level == LoggingVerbosity.WARNING:
        _logger.setLevel(logging.WARNING)
    elif level == LoggingVerbosity.INFO:
        _logger.setLevel(logging.INFO)
    elif level >= LoggingVerbosity.DEBUG:
        _logger.setLevel(logging.DEBUG)


drim2p.add_command(convert.convert)
drim2p.add_command(motion.motion)
drim2p.add_command(draw.draw)
drim2p.add_command(extract.extract)
drim2p.add_command(deltaf.deltaf)


if __name__ == "__main__":
    drim2p(sys.argv[1:])
