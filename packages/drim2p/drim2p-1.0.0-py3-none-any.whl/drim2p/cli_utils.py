# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

import logging
from typing import Any

import click

_logger = logging.getLogger(__name__)


def noop_if_missing(
    context: click.Context, parameter: click.Parameter, value: Any
) -> Any:
    """Exits the current context if the given value is `None`, else does nothing.

    This should be used as the callback of a `click.Parameter` when a `None` value for
    that parameter should cause the command to NO-OP.

    See `click`'s official documentation for rationale:
    https://github.com/pallets/click/blob/2d610e36a429bfebf0adb0ca90cdc0585f296369/docs/arguments.rst?plain=1#L43

    Args:
        context (click.Context): Current command context.
        parameter (click.Parameter): Parameter for which this is a callback.
        value (Any): Value to validate.

    Returns:
        The value unchanged, guaranteed not to be `None`.
    """
    if value is None:
        _logger.debug(
            f"Parameter '{parameter.human_readable_name}' "
            f"of command '{context.command.name}' received a `None` value "
            f"which was marked as a NO-OP."
        )
        context.exit(0)

    return value
