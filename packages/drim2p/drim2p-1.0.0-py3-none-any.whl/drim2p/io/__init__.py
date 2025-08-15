# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

import logging
import pathlib
import re
from collections.abc import Iterable
from typing import Any
from typing import Literal
from typing import get_args

import h5py
import numpy as np

from drim2p.io.errors import SeparatorTooLongError
from drim2p.io.errors import UnknownCompressionError

_logger = logging.getLogger(__name__)

COMPRESSION = Literal["gzip", "lzf"]


def collect_paths_from_extensions(
    root: pathlib.Path,
    extensions: Iterable[str],
    recursive: bool = False,
    strict: bool = False,
) -> list[pathlib.Path]:
    """Collects paths from a root path based on extensions.

    Args:
        root (pathlib.Path):
            Root path to start the search from. If this is a file, it is the only path
            for which the extension is matched.
        extensions (Iterable[str]):
            Extensions to check against. By default, any file that contains one of these
            in its suffixes will be matched. See `strict` for a different behaviour.
        recursive (bool, optional):
            Whether to recursively visit directories when searching.
        strict (bool, optional):
            Whether to force checked files to only have a single suffix. By default, the
            checked extensions can appear anywhere in the suffix list of files.

    Returns:
        A list of the matched pats.
    """

    def have_at_least_one_common_element(
        iterable1: Iterable[str], iterable2: Iterable[str]
    ) -> bool:
        """Returns whether at least one element is common to both iterables.

        This matches each item of iterable1 against all those of iterable2 and computes
        whether they are the same, then returns if at least one of the matches is True.

        Returns:
            Whether at least one element is common to both iterables.
        """
        return any(x in iterable2 for x in iterable1)

    collected = []

    if root.is_file():
        if have_at_least_one_common_element(
            extensions, [root.suffix] if strict else root.suffixes
        ):
            collected = [root]
        return collected

    for path in root.iterdir():
        if path.is_dir():
            if not recursive:
                continue

            collected.extend(
                collect_paths_from_extensions(path, extensions, recursive, strict)
            )
        elif have_at_least_one_common_element(
            extensions, [path.suffix] if strict else path.suffixes
        ):
            collected.append(path)

    return collected


def filter_paths(
    paths: Iterable[pathlib.Path],
    include: str | None = None,
    exclude: str | None = None,
    separator: str = ";",
) -> list[pathlib.Path]:
    """Filters paths based on include and exclude strings.

    The order of operation first includes paths using the `include` filters then
    excludes paths using the `exclude` filters.
    If `include` is `None`, all paths are considered included before applying exclusion
    filters. If `exclude` is `None`, all paths included by `include` are returned. If
    both are `None`, all paths are returned.

    Args:
        paths (Iterable[pathlib.Path]): Paths to filter.
        include (str | None, optional):
            String of the include filters separated by `separator`.
        exclude (str | None, optional):
            String of the exclude filters separated by `separator`.
        separator (str, optional):
            A single-character separator used to separate different filters.

    Returns:
        A list of the paths as filtered by the input filters.

    Examples:
        >>> paths = [
        ...     Path("path123"),
        ...     Path("path234"),
        ...     Path("path345"),
        ...     Path("path456"),
        ... ]
        >>> include = "1;2;3"
        >>> exclude = "34"

        >>> filter_paths(paths, include=include)
        [Path('path123'), Path('path234'), Path('path345')]

        >>> filter_paths(paths, exclude=exclude)
        [Path('path123'), Path('path456')]

        >>> filter_paths(paths, include, exclude)
        [Path('path123')]
    """
    # NO-OP if neither include nor exclude is set
    if include is None and exclude is None:
        return list(paths)

    include = None if include is None else split_string(include, separator)
    exclude = None if exclude is None else split_string(exclude, separator)

    # First, filter which paths should be included based on `include` and `strict`
    included = list(paths)
    if include is not None:
        included = []
        for path in paths:
            for filter_ in include:
                if re.findall(filter_, str(path)):
                    included.append(path)
                    break

    # Then, exclude any path previously selected if it matches an `exclude`
    filtered = included
    if exclude is not None:
        filtered = []
        for path in included:
            for filter_ in exclude:
                if re.findall(filter_, str(path)):
                    break
                filtered.append(path)

    return filtered


def find_paths(
    root: pathlib.Path,
    extensions: Iterable[str],
    include: str | None = None,
    exclude: str | None = None,
    recursive: bool = False,
    strict: bool = False,
) -> list[pathlib.Path]:
    """Collects and filters paths found in a directory.

    Args:
        root (pathlib.Path):
            Path to the root path. If this is a file, it is the only file filtered. If
            it is a directory, files are collected then filtered from it. If 'recursive'
            is set, it is traversed recursively.
        extensions (Iterable[str]):
            Extensions to check against. By default, any file that contains one of these
            in its suffixes will be matched. See `strict` for a different behaviour.
        include (str | None, optional):
            String of the include filters separated by `separator`.
        exclude (str | None, optional):
            String of the exclude filters separated by `separator`.
        recursive (bool, optional):
            Whether to recursively visit directories when searching.
        strict (bool, optional):
            Whether to force checked files to only have a single suffix. By default, the
            checked extensions can appear anywhere in the suffix list of files.

    Returns:
        A list of the paths collected and after filtering.
    """
    _logger.debug(
        f"Collecting files (extensions: {', '.join(extensions)} - include: {include} - "
        f"exclude: {exclude})."
    )

    paths = [root]
    if root.is_dir():
        paths = collect_paths_from_extensions(root, extensions, recursive, strict)

    paths = filter_paths(paths, include, exclude)

    _logger.debug(f"Collected {len(paths)} paths.")

    return paths


def get_h5py_compression_parameters(
    compression: COMPRESSION | None, compression_opts: int | None = None
) -> tuple[COMPRESSION | None, int | None, bool]:
    """Returns compression parameters for the given compression.

    Args:
        compression (COMPRESSION | None): Compression algorithm to use.
        compression_opts (int | None, optional): Compression algorithm options.

    Returns:
        A tuple of (compression, compression_opts, shuffle) where `compression` is a
        valid compression value for `h5py.Group.create_dataset`, acompression_optsa is
        a valid aggression level for 'gzip' compression and `None` otherwise, and
        `shuffle` is whether to do byte-shuffling (only enabled for 'lzf' compression).

    Raises:
        UnknownCompressionError: If the compression is not supported.
    """
    if compression is None:
        compression_opts = None
        shuffle = False
    elif compression == "gzip":
        compression_opts = compression_opts or 4
        shuffle = False
    elif compression == "lzf":
        compression_opts = None
        shuffle = True
    else:
        raise UnknownCompressionError(compression, (*get_args(COMPRESSION), None))

    return compression, compression_opts, shuffle


def group_paths_by_regex(
    paths: list[pathlib.Path], group_by_regex: str
) -> list[list[pathlib.Path]]:
    """Groups paths based on the match of `group_by_regex` against their stems.

    Paths that do not contain the regex are put in their own size 1 group.

    Args:
        paths (list[pathlib.Path]): Paths to group.
        group_by_regex (str): Regex to use when matching.

    Returns:
        A list of path groups. Groups are guaranteed to have at least one element.
    """
    matches = [re.findall(group_by_regex, path.stem) for path in paths]
    groups: dict[str, list[pathlib.Path]] = {}
    for match, path in zip(matches, paths, strict=True):
        if len(match) == 0:
            # If no matches found, default to a group of size 1 with the current path
            match.append(path.stem)
        match = match[0]  # noqa: PLW2901

        groups[match] = [*groups.get(match, []), path]

    return list(groups.values())


def read_rois_and_shapes(
    root: h5py.Group,
) -> tuple[list[np.ndarray[Any, np.dtype[np.number]]], list[str]]:
    """Reads ROI arrays and shapes from an HDF5 group.

    Args:
        root (h5py.Group): Group that contains the ROIs and their shapes.

    Returns:
        A tuple of (rois, shapes) where `rois` is a list of NumPy arrays containing the
        vertices of the ROIs (of shape (X, 2) where X is the number of ROIs), and
        `shapes` is a list of string values for the shapes of the ROIs.
    """
    rois = []
    roi_shape_types = []
    roi_group = root.get("ROIs")
    if roi_group is None:
        _logger.debug("No ROIs found.")
    else:
        _logger.debug("Found existing ROIs.")
        rois = [roi[:] for name, roi in roi_group.items() if name != "roi_shape_types"]

        roi_shape_types = roi_group.get("roi_shape_types")
        if roi_shape_types is None:
            _logger.error(
                "Failed to retrieve ROIs shape types. Assuming all rectangles."
            )
            roi_shape_types = ["rectangle"] * len(rois)
        else:
            # h5py returns the values as a NumPy array of bytes
            roi_shape_types = roi_shape_types[:].astype(str).tolist()

    return rois, roi_shape_types


def split_string(string: str, separator: str = ";") -> list[str]:
    r"""Splits a string on non-escaped `separator` occurrences.

    Args:
        string (str): String to split.
        separator (str, optional): A single-character separator to split on.

    Returns:
        A list containing the substrings after splitting.

    Raises:
        SeparatorTooLongError: If the separator is longer than a single character.

    Examples:
        >>> split_string("foo;bar")
        ['foo', 'bar']

        >>> split_string(r"foo;b\;ar")
        ['foo', 'b\\;ar']  # Note that printing the second item shows 'b\;ar'

        >>> split_string("foo bar foo\ bar", " ")
        ['foo', 'bar', 'foo\\;bar']
    """
    if len(separator) > 1:
        raise SeparatorTooLongError(separator)

    return re.split(
        rf"(?<!(?<!\\)\\){separator}", string
    )  # Only split on separators that are not escaped, while allowing "\\{separator}"
