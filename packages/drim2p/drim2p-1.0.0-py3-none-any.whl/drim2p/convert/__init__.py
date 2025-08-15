# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

import click

from drim2p.convert import raw as raw_convert


@click.group()
def convert() -> None:
    """Converts data to HDF5/NWB."""


convert.add_command(raw_convert.convert_raw_command)
