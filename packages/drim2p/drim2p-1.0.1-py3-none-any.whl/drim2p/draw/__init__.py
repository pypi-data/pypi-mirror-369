# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

import click

import drim2p.draw.roi as draw_roi


@click.group
def draw() -> None:
    """Allows for drawing ROIs on HDF5 dataset."""


draw.add_command(draw_roi.draw_roi_command)
