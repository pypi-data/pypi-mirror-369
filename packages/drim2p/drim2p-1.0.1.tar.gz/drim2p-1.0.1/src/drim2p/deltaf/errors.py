# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

from collections.abc import Sequence
from typing import Any


class ArrayDimensionNotSupportedError(Exception):
    """Array is neither 1- or 2D.

    Args:
        dimension (int): Invalid dimensionality.
    """

    def __init__(self, dimension: int) -> None:
        super().__init__(f"Only 1- and 2D arrays are supported. Found: {dimension}D.")


class InvalidPercentileError(Exception):
    """Percentile is not a valid integer.

    Args:
        value (Any): Invalid percentile.
    """

    def __init__(self, value: Any) -> None:
        super().__init__(f"Cannot compute percentile when it is `{value}`.")


class OutOfRangePercentileError(Exception):
    """Percentile is outside of the range 0 to 100 inclusive.

    Args:
        percentile (int): Invalid percentile.
    """

    def __init__(self, percentile: int) -> None:
        super().__init__(
            f"Percentile should be between 0 and 100. Found: {percentile}. "
        )


class RollingWindowTooLargeError(Exception):
    """Windows width is larger than twice the first dimension of the input minus one.

    Args:
        window_width (int): Invalid window width.
        array_length (int): Length of the first dimension of the input array.
    """

    def __init__(self, window_width: int, array_length: int) -> None:
        super().__init__(
            f"Rolling window width should be at most twice the length of the first "
            f"dimension of the input minus 1. Got '{window_width}' which is larger "
            f"than {array_length * 2 - 1}."
        )


class UnknownMethodError(Exception):
    """Given method for computing F0 is unknown.

    Args:
        method (str): Unknown method.
        known (Sequence[str]): Known methods.
    """

    def __init__(self, method: str, known: Sequence[str]) -> None:
        super().__init__(
            f"Unknown method: '{method}'. Valid methods are: {', '.join(known)}"
        )


class UnknownPaddingModeError(Exception):
    """Given padding mode is unknown.

    Args:
        padding_mode (str): Unknown padding mode.
        known (Sequence[str]): Known padding modes.
    """

    def __init__(self, padding_mode: str, known: Sequence[str]) -> None:
        super().__init__(
            f"Unknown padding mode '{padding_mode}'. "
            f"Valid modes are: {', '.join(known)}."
        )
