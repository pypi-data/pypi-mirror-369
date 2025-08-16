# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
import enum
import pathlib
import tomllib
from collections.abc import Sequence
from typing import Any
from typing import cast

import pydantic


class ConfigKeyNotFoundError(Exception):
    """Config key is missing.

    Args:
        key (str): Missing key.
    """

    def __init__(self, key: str) -> None:
        super().__init__(f"Could not find a config entry for key '{key}'.")


class InvalidConfigValueError(Exception):
    """Value for the given key is not valid.

    Args:
        key (str): Key of the given value.
        value (Any): Invalid value.
        valid (Sequence[str]):
            Sequence of valid values. This can be a sequence with a single value
            explaining what kind of value is expected.
    """

    def __init__(self, key: str, value: Any, valid: Sequence[str]) -> None:
        super().__init__(
            f"Invalid value '{value}' for key '{key}'. "
            f"Valid values are: {' '.join(valid)}"
        )


class InvalidMotionConfigFileError(Exception):
    """TOML file is not valid as a motion config as it is missing the proper section.

    Args:
        path (pathlib.Path): Path to the TOML file.
    """

    def __init__(self, path: pathlib.Path) -> None:
        super().__init__(
            f"Failed to parse TOML file: file does not have a "
            f"'motion-correction' section. ({path})"
        )


class Strategy(enum.Enum):
    """Motion correction strategy."""

    Markov = "HiddenMarkov2D"
    Plane = "PlaneTranslation2D"
    Fourier = "DiscreteFourier2D"

    @classmethod
    def _missing_(cls, value: Any) -> Any:
        try:
            value = value.lower()
        except AttributeError:
            return super()._missing_(value)

        for variant in cls:
            if variant.name.lower() == value:
                return variant

        return super()._missing_(value)


class MotionConfig(pydantic.BaseModel):
    """Motion correction config."""

    strategy: Strategy = Strategy.Fourier
    displacement: tuple[int, int] = (50, 50)

    @classmethod
    def from_file(cls, path: pathlib.Path) -> MotionConfig:
        """Creates a motion correction config from a TOML file.

        Args:
            path (pathlib.Path): Path to the TOML file to parse.

        Returns:
            A motion correction object containing the information from the given TOML
            file.

        Raises:
            InvalidMotionConfigFileError:
                If the TOML file does not have 'motion-correction' section.
        """
        with path.open("rb") as handle:
            contents = tomllib.load(handle)

        dictionary = contents.get("motion-correction")
        if dictionary is None:
            raise InvalidMotionConfigFileError(path)

        return cls.from_dictionary(dictionary)

    @classmethod
    def from_dictionary(cls, dictionary: dict[str, Any]) -> MotionConfig:
        """Parses a motion config from a dictionary.

        Args:
            dictionary (dict[str, Any]): Dictionary to parse as a motion config.

        Returns:
            A motion config containing the information from the given dictionary.

        Raises:
            ConfigKeyNotFoundError: If one of the required config keys is missing.
            InvalidConfigValueError: If one of the required config values is invalid.
        """
        strategy = dictionary.get("strategy")
        if strategy is None:
            raise ConfigKeyNotFoundError("strategy")  # noqa: EM101
        try:
            strategy = Strategy(strategy)
        except ValueError:
            raise InvalidConfigValueError(
                "strategy",  # noqa: EM101
                strategy,
                [variant.name for variant in Strategy],
            ) from None

        displacement = dictionary.get("displacement")
        if displacement is None:
            raise ConfigKeyNotFoundError("displacement")  # noqa: EM101
        # Displacement should be two values, [X, Y]
        if not hasattr(displacement, "__len__") or len(displacement) != 2:  # noqa: PLR2004
            raise InvalidConfigValueError(
                "displacement",  # noqa: EM101
                displacement,
                ["any two integer values"],
            )
        try:
            displacement = cast("tuple[int, int]", tuple(map(int, displacement)))
        except ValueError:
            raise InvalidConfigValueError(
                "displacement",  # noqa: EM101
                displacement,
                ["any two integer values"],
            ) from None

        return cls(strategy=strategy, displacement=displacement)


class NotesEntry(pydantic.BaseModel):
    """Notes entry from a `.notes.txt` files for a recording session."""

    start_time: datetime.datetime
    """Start time of the notes entry recording."""
    end_time: datetime.datetime
    """End time of the notes entry recording."""
    file_path: pathlib.Path
    """File path the notes entry relates to."""

    @property
    def timedelta(self) -> datetime.timedelta:
        """Time delta between the entry's end and start times."""
        return self.end_time - self.start_time

    @property
    def timedelta_ms(self) -> float:
        """Time delta in milliseconds between the entry's end and start times."""
        return self.timedelta / datetime.timedelta(milliseconds=1)

    @property
    def pure_file_path(self) -> pathlib.PureWindowsPath:
        """A Windows file path representation of file path."""
        return pathlib.PureWindowsPath(self.file_path)
