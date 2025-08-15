# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

import logging
import pathlib
from typing import Any
from typing import Literal
from typing import get_args

import click
import h5py
import numpy as np
import numpy.typing as npt

from drim2p import cli_utils
from drim2p import io
from drim2p.deltaf.errors import ArrayDimensionNotSupportedError
from drim2p.deltaf.errors import InvalidPercentileError
from drim2p.deltaf.errors import OutOfRangePercentileError
from drim2p.deltaf.errors import RollingWindowTooLargeError
from drim2p.deltaf.errors import UnknownMethodError
from drim2p.deltaf.errors import UnknownPaddingModeError

_logger = logging.getLogger(__name__)

_1Dimensional = 1
_2Dimensional = 2

_F0Method = Literal["percentile", "mean", "median"]
_PaddingMode = Literal["constant", "reflect", "wrap", "edge"]


@click.command
@click.argument(
    "source",
    required=False,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        path_type=pathlib.Path,
    ),
    callback=cli_utils.noop_if_missing,
)
@click.option(
    "-m",
    "--method",
    required=False,
    type=click.Choice(get_args(_F0Method)),
    default="percentile",
    help="Computation method for f₀.",
)
@click.option(
    "-p",
    "--percentile",
    required=False,
    type=click.INT,
    default=5,
    help=(
        "Percentile to use when computing f₀ using the 'percentile' method. Ignored if "
        "computing with a different method."
    ),
)
@click.option(
    "-w",
    "--window-width",
    required=False,
    type=click.INT,
    default=0,
    help=(
        "Rolling window width in frames to use when computing f₀. Pass 0 to disable "
        "it (default). If greater than 0, the window is used to compute a running "
        "value of f₀ for each timepoint of the input, with padding applied according "
        "to '--padding' around the edges. If greater than 0, the rolling window should "
        "be less than twice the size of the first dimension of the input minus 1."
    ),
)
@click.option(
    "--padding",
    "padding_mode",
    required=False,
    type=click.Choice(get_args(_PaddingMode)),
    default="constant",
    help="Mode to use when padding the input. Ignored if '--window-width' is 0.",
)
@click.option(
    "--padding-value",
    "constant_value",
    required=False,
    type=click.INT,
    default=0,
    help=(
        "Constant value to use when padding using 'constant' mode. Ignored if "
        "'--padding' is not 'constant'."
    ),
)
@click.option(
    "-r",
    "--recursive",
    required=False,
    is_flag=True,
    help="Whether to search directories recursively when looking for files.",
)
@click.option(
    "-i",
    "--include",
    required=False,
    default=None,
    help=(
        "Include filters to apply when searching for files. This supports regular "
        "expressions. Include filters are applied before any exclude filters. They "
        "should be a semi-colon-separated string of filters (e.g., 'foo;bar' contains "
        "two filters, 'foo' and 'bar')."
    ),
)
@click.option(
    "-e",
    "--exclude",
    required=False,
    default=None,
    help=(
        "Exclude filters to apply when searching for files. This supports regular "
        "expressions. Exclude filters are applied after all include filters. They "
        "should be a semi-colon-separated string of filters (e.g., 'foo;bar' contains "
        "two filters, 'foo' and 'bar')."
    ),
)
@click.option(
    "--force",
    required=False,
    is_flag=True,
    help="Whether to overwrite output files if they exist.",
)
def deltaf(**kwargs: Any) -> None:
    """Computes ΔF/F₀ for extracted signals.

    Input arrays should be 1- or 2D arrays, where the first dimension is the one along
    which to compute f₀.

    If given a rolling window width, f₀ is computed for each entry along the first
    dimension of the input array. For values around the edges (within half of window
    width), the array is padded using the provided method (default is padding with
    0s). Because of this, choosing a window that is too large can produce some
    unexpected values far into the array.
    """
    compute_dff(**kwargs)


def compute_dff(
    source: pathlib.Path,
    method: _F0Method = "percentile",
    percentile: int = 5,
    window_width: int = 0,
    padding_mode: _PaddingMode = "constant",
    constant_value: int = 0,
    recursive: bool = False,
    include: str | None = None,
    exclude: str | None = None,
    force: bool = False,
) -> None:
    """Computes ΔF/F₀ for extracted signals.

    Input arrays should be 1- or 2D arrays, where the first dimension is the one along
    which to compute f₀.

    If given a rolling window width, f₀ is computed for each entry along the first
    dimension of the input array. For values around the edges (within half of window
    width), the array is padded using the provided method (default is padding with
    0s). Because of this, choosing a window that is too large can produce some
    unexpected values far into the array.

    Args:
        source (pathlib.Path):
            Source file or directory to process. If a directory, the default is to look
            look for files inside of it without recursion.
        method (_F0Method, optional): Computation method for f₀.
        percentile (int, optional):
            Percentile to use when computing f₀ using the percentile method. Ignored if
            computing with a different method.
        window_width (int, optional):
            Rolling window width in frames to use when computing f₀. Pass 0 to disable
            it (default). If greater than 0, the window is used to compute a running
            value of f₀ for each timepoint of the input, with padding applied according
            to `padding_mode` around the edges. If greater than 0, the rolling window
            should be less than twice the size of the first dimension of the input minus
            1.
        padding_mode (_PaddingMode, optional):
            Mode to use when padding the input. Ignored if 'window_width' is 0.
        constant_value (int, optional):
            Constant value to use when padding using 'constant' mode. Ignored if
            'padding_mode' is not 'constant'.
        recursive (bool, optional):
            Whether to search directories recursively when looking for files.
        include (str | None, optional):
            Include filters to apply when searching for files. This supports regular
            expressions. Include filters are applied before any exclude filters. They
            should be a semi-colon-separated string of filters (e.g., 'foo;bar' contains
            two filters, 'foo' and 'bar').
        exclude (str | None, optional):
            Exclude filters to apply when searching for files. This supports regular
            expressions. Exclude filters are applied after all include filters. They
            should be a semi-colon-separated string of filters (e.g., 'foo;bar' contains
            two filters, 'foo' and 'bar').
        force (bool, optional): Whether to overwrite output files if they exist.
    """
    for path in io.find_paths(source, [".h5"], include, exclude, recursive, True):
        _logger.info(f"Computing ΔF/F₀ for '{path}'.")
        _logger.debug(f"Opening handle for '{path}'.")
        handle = h5py.File(path, "a", locking=False)

        # Retrieve signal group
        signals_group = handle.get("extracted")
        if signals_group is None:
            _logger.error(
                f"Could not find group 'extracted' inside of '{path}'. "
                f"Available groups are: {list(handle)}. Skipping file."
            )
            continue

        # Check for existing ΔF/F₀
        delta_f_group = handle.get("delta_f")
        if delta_f_group is None:
            delta_f_group = handle.create_group("delta_f")
        elif delta_f_group is not None and not force:
            _logger.info(
                f"ΔF/F₀ group already exists in '{path}' and 'force' was not set. "
                f"Skipping file."
            )
            continue

        # Process signals
        for name in signals_group:
            signals = signals_group[name]

            # Compute ΔF/F₀
            f0 = compute_f0(
                # TODO: Maybe use a dask.Array if we run into memory problems
                signals[:].T,  # Signals are stored as (signal, timepoint)
                method,
                percentile,
                window_width,
                padding_mode,
                constant_value,
            )

            # Convert F0 to something compatible with `signals`' shape
            if len(f0.shape) == 1:
                f0 = f0[np.newaxis]
            f0 = f0.T

            # Compute ΔF/F₀
            delta_f = signals - f0
            dff = delta_f / f0

            # Write result
            delta_f_group[name] = dff

        _logger.info("Saved ΔF/F₀.")


def compute_f0(
    array: npt.NDArray[Any],
    method: _F0Method = "percentile",
    percentile: int = 5,
    window_width: int = 0,
    padding_mode: _PaddingMode = "constant",
    constant_value: int = 0,
) -> npt.NDArray[Any]:
    """Computes f₀ for a given array of signals.

    Args:
        array (npt.NDArray[Any]):
            Array to compute f₀ for. The first dimension should be time.
        method (_F0Method, optional): Computation method for f₀.
        percentile (int, optional):
            Percentile to use when computing f₀ using the percentile method.
        window_width (int, optional):
            Rolling window width to use when computing f₀. Pass 0 to disable it. If
            greater than 0, the window is used to compute a running value of f₀ for
            each timepoint of the input, with padding applied according to
            'padding_mode' around the edges. If greater than 0, the rolling window
            should be less than twice the size of the first dimension of the input
            minus 1.
        padding_mode (_PaddingMode, optional):
            Mode to use when padding the input. Ignored if 'window_width' is 0.
        constant_value (int, optional):
            Constant value to use when padding using 'constant' mode. Ignored if
            'window_width' is 0.

    Returns:
        The F0 value for the input array. This is a 0D array if the input is 1D and
        no rolling window was provided. This is ND, where N is the dimensionality of
        the input, if a rolling window was provided.

    Raises:
        ArrayDimensionNotSupportedError: If the input array is not 1- or 2D.
        OutOfRangePercentileError: If the percentile is not between 0 and 100 inclusive.
        RollingWindowTooLargeError:
            If the rolling window is larger than the first dimension of the input minus
            1.
        UnknownMethodError: If given an unknown method for computing F0.
        UnknownPaddingModeError: If given an unknown padding mode.
    """
    # Ensure data is 2D
    got_1d_in = False
    if len(array.shape) > _2Dimensional or len(array.shape) < _1Dimensional:
        raise ArrayDimensionNotSupportedError(len(array.shape))
    elif len(array.shape) == 1:
        got_1d_in = True
        array = array.reshape(-1, 1)

    if method == "percentile":
        if not 0 <= percentile <= 100:  # noqa: PLR2004
            raise OutOfRangePercentileError(percentile)
    # 'median' is a convenience method for percentile=50
    elif method == "median":
        method = "percentile"
        percentile = 50
    elif method not in get_args(_F0Method):
        raise UnknownMethodError(method, get_args(_F0Method))

    # No rolling window, compute single value along first axis and be done
    if window_width <= 0:
        result = _compute_f0(array, method, percentile)

        # Only squeeze when input was 1D (i.e., don't squeeze if we got 2D with one or
        # more dimension(s) of size 1).
        if got_1d_in:
            result = result.squeeze()
        return result

    # We have a rolling window
    # Ensure the rolling window is small enough
    if window_width > array.shape[0] * 2 - 1:
        raise RollingWindowTooLargeError(window_width, array.shape[0])

    # Ensure the window_width is odd so that it can be applied on integer indices
    if window_width % 2 == 0:
        window_width += 1

    # Pad the input so that we can compute a value for all indices that are less
    # than half of the window_width. We can't normally compute them as the window
    # does not have enough information around the edges.
    if padding_mode not in get_args(_PaddingMode):
        raise UnknownPaddingModeError(padding_mode, get_args(_PaddingMode))
    # Passing kwarg `constant_values` for methods other than "constant" raises a
    # ValueError.
    kwargs = {}
    if padding_mode == "constant":
        kwargs["constant_values"] = constant_value

    padded = np.pad(
        array,
        ((window_width // 2, window_width // 2), (0, 0)),
        padding_mode,
        **kwargs,
    )  # type: ignore[call-overload]

    # Make windows into the padded array. Using strides allows us to easily drag a
    # window along the time dimension with shape (window_width, *rest_of_shape), one
    # timepoint at at time.
    windows = np.lib.stride_tricks.as_strided(
        padded,
        (array.shape[0], window_width, padded.shape[-1]),
        # Duplicate the first stride so we slide the window one index in the first
        # dimension at a time.
        (padded.strides[0], *padded.strides),
    )

    # Compute and collect the results
    results = np.empty(array.shape, np.float64)
    for i, window in enumerate(windows):
        results[i] = _compute_f0(window, method, percentile)

    # Only squeeze when input was 1D (i.e., don't squeeze if we got 2D with one
    # dimension of size 1).
    if got_1d_in:
        results = results.squeeze()
    return results


def _compute_f0(
    array: npt.NDArray[Any], method: _F0Method, percentile: int | None
) -> npt.NDArray[Any]:
    f0: npt.NDArray[Any]
    if method == "percentile":
        if percentile is None:
            raise InvalidPercentileError(percentile)
        f0 = np.percentile(array, percentile, axis=0)
    elif method == "mean":
        f0 = np.mean(array, axis=0)

    return f0
