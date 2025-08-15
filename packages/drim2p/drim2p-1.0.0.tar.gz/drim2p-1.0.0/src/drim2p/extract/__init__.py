# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

import click

from drim2p.extract import signal


@click.group()
def extract() -> None:
    """Extracts signals."""


extract.add_command(signal.extract_signal_command)
