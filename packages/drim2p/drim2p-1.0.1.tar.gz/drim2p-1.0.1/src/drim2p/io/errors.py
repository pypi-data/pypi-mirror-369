# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

import pathlib
from collections.abc import Sequence


class NoINISectionsFoundError(Exception):
    """INI file did not contain any section ([DEFAULT] excepted).

    Args:
        path (pathlib.Path): Path to the INI file.
    """

    def __init__(self, path: pathlib.Path) -> None:
        super().__init__(f"Failed to parse INI metadata: no sections found. ({path})")


class TooManyINISectionsFoundError(Exception):
    """INI file contained too many sections ([DEFAULT] excepted).

    Args:
        path (pathlib.Path): Path to the INI file.
    """

    def __init__(self, path: pathlib.Path, sections: Sequence[str]) -> None:
        super().__init__(
            f"Failed to parse INI metadata: too many sections found. Only a single "
            f"section (other than [DEFAULT]) is supported. "
            f"Found: {' '.join(sections)}. ({path})"
        )


class SeparatorTooLongError(Exception):
    """Given separator is longer than a single character.

    Args:
        separator (str): Separator received.
    """

    def __init__(self, separator: str) -> None:
        super().__init__(f"Separator should be a single character. Found: {separator}.")


class UnknownCompressionError(Exception):
    """Requested compression is unknown.

    Args:
        compression (str): Compression requested.
        known (Sequence[str]): Known compression values.
    """

    def __init__(self, compression: str, known: Sequence[str]) -> None:
        super().__init__(
            f"Unknown compression: '{compression}'. "
            f"Valid compression algorithms are: {', '.join(known)}"
        )
