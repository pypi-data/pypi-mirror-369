# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

import configparser
import datetime
import pathlib
import re
import warnings
from typing import Any

import numpy as np

from drim2p import models
from drim2p.io.errors import NoINISectionsFoundError
from drim2p.io.errors import TooManyINISectionsFoundError

NOTES_ENTRY_PATTERN = re.compile(r"^-+$\n((?:.|\n)+?)\n^-+$\n", flags=re.MULTILINE)
"""Pattern of a notes entry. It consists of lines of text between two lines of '-'s."""


def parse_metadata_from_ome(
    xml: pathlib.Path | str,
) -> tuple[tuple[int, int, int], np.dtype[np.number]]:
    """Parses type and shape information of a RAW file from its OME-XML metadata.

    Args:
        xml (pathlib.Path | str):
            Path to the OME-XML metadata or a string of the metadata.

    Returns:
        A tuple of the (`shape`, `dtype``) of the RAW file, where `shape` is the shape
        in ZYX order, and `dtype` is the numpy data type with the correct byte order.
    """
    # Lazy time-consuming import
    import ome_types

    # Silence `UserWarning`s for potentially invalid IDs that are automatically cast
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        ome = ome_types.from_xml(xml)
    pixels = ome.images[0].pixels

    shape = pixels.size_t, pixels.size_y, pixels.size_x
    dtype = np.dtype(pixels.type.numpy_dtype).newbyteorder(
        ">" if pixels.big_endian else "<"
    )

    return shape, dtype


def parse_ini_config_as_typed(
    config: dict[str, str],
) -> dict[str, int | float | bool | str]:
    """Parses a dictionary of INI key-value pairs and returns a typed version.

    Note, this assumes that the config dictionary was read using `configparser` and
    that all values are strictly coercible to integers, floats, booleans, or strings.

    Args:
        config (dict[str, str]): Config dictionary to parse.

    Returns:
        The typed version of the dictionary.
    """
    typed: dict[str, int | float | bool | str] = {}

    for key, value in config.items():
        # Integers
        if value.isnumeric():
            typed[key] = int(value)
            continue

        # Floats
        if re.fullmatch(r"^[0-9.-]+$", value):
            typed[key] = float(value)
            continue

        # Booleans
        if value in {"FALSE", "TRUE"}:
            typed[key] = value == "TRUE"
            continue

        # Strings
        typed[key] = value[1:-1]

    return typed


def parse_metadata_from_ini(
    ini_path: pathlib.Path, typed: bool = False
) -> dict[str, Any]:
    """Parses metadata from an INI file.

    Args:
        ini_path (pathlib.Path): Path to the INI file.
        typed (bool, optional): Whether to parse the values as typed.

    Returns:
        The config dictionary, as either `dict[str, str]` if untyped, or
        `dict[str, Any]` if typed.

    Raises:
        NoINISectionsFoundError:
            If the INI file does not contain any sections ([DEFAULT] excluded).
        TooManyINISectionsFoundError:
            If the INI file contains more than one section ([DEFAULT] excluded).
    """
    parser = configparser.ConfigParser()
    parser.read(ini_path)

    sections = parser.sections()
    if len(sections) < 1:
        raise NoINISectionsFoundError(ini_path)
    elif len(sections) > 1:
        raise TooManyINISectionsFoundError(ini_path, sections)
    section = sections[0]

    config = dict(parser[section])
    return config if not typed else parse_ini_config_as_typed(config)


def parse_notes_entries(text: str) -> list[models.NotesEntry]:
    """Parses notes entries from a text.

    Args:
        text (str): Text containing the notes entries to parse.

    Returns:
        A list of entries as `models.NotesEntry`s.
    """
    entry_strings = re.findall(NOTES_ENTRY_PATTERN, text)

    entries = []
    for string in entry_strings:
        start_time, _, file_path, *_, end_time = string.split("\n")

        entries.append(
            models.NotesEntry(
                start_time=datetime.datetime.fromisoformat(start_time),
                file_path=pathlib.Path(file_path),
                end_time=datetime.datetime.fromisoformat(end_time),
            )
        )

    return entries


def read_raw_as_numpy(
    path: pathlib.Path,
    shape: tuple[int, ...],
    dtype: np.dtype[np.number],
) -> np.ndarray[Any, np.dtype[np.number]]:
    """Reads a RAW file from disk and returns it as a numpy array.

    Args:
        path (pathlib.Path): Path to the RAW file.
        shape (tuple[int, ...]): Shape of the RAW file.
        dtype (np.dtype[np.number]):
            Data type of the RAW file with the correct endianness.

    Returns:
        A numpy array made from the RAW data as `dtype` type and reshaped to `shape`.
    """
    return np.fromfile(path, dtype=dtype).reshape(shape)
