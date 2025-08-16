# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

import click

from drim2p.motion import correct


@click.group()
def motion() -> None:
    """Handles motion correction."""


motion.add_command(correct.apply_motion_correction_command)
