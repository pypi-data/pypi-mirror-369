# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

import logging
import pathlib
from typing import Any

import click
import h5py

from drim2p import cli_utils
from drim2p import io

_logger = logging.getLogger(__name__)


@click.command("signal")
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
    "--group-by-regex",
    required=False,
    default=None,
    help=(
        "Regular expression to use when grouping SOURCEs together. This results in the "
        "paths being preprocessed together based on the regex. This is ignored if "
        "SOURCE is a single file. Note that using this can lead to a very high memory "
        "usage depending on how many chunks needs to be loaded. Also note that for "
        "grouping to work, grouped files should have the same number of ROIs."
    ),
)
@click.option(
    "-d",
    "--dataset",
    "dataset_name",
    required=False,
    default="imaging",
    help="Name of the HDF5 dataset to display for ROI drawing.",
)
@click.option(
    "-r",
    "--recursive",
    required=False,
    is_flag=True,
    help="Whether to search directories recursively when looking for HDF5 files.",
)
@click.option(
    "-i",
    "--include",
    required=False,
    default=None,
    help=(
        "Include filters to apply when searching for HDF5 files. "
        "This supports regular-expressions. Include filters are applied before any "
        "exclude filters."
    ),
)
@click.option(
    "-e",
    "--exclude",
    required=False,
    default=None,
    help=(
        "Exclude filters to apply when searching for HDF5 files. "
        "This supports regular-expressions. Exclude filters are applied after all "
        "include filters."
    ),
)
@click.option(
    "--dont-abort-on-skipped-file",
    required=False,
    is_flag=True,
    help=(
        "Whether to keep working on a group if one or more of its files is skipped for "
        "any reason (e.g., file was already preprocessed by '--force' is not set)."
    ),
)
@click.option(
    "--force",
    required=False,
    is_flag=True,
    help="Whether to overwrite output files if they exist.",
)
def extract_signal_command(**kwargs: Any) -> None:
    """Extracts decontaminated signals from ROIs.

    Note that SOURCE can be either a single file or a directory. If it is a directory,
    all the HDF5 files it contains will be converted.

    By default, all provided files are treated as separate sessions. In order to process
    files together, use 'group-by-regex' to group paths together based on a regular
    expression. If you wish to group all files together, pass an empty string as the
    regular expression.
    """
    extract_signal(**kwargs)


def extract_signal(
    source: pathlib.Path,
    group_by_regex: str | None = None,
    dataset_name: str = "imaging",
    recursive: bool = False,
    include: str | None = None,
    exclude: str | None = None,
    dont_abort_on_skipped_file: bool = False,
    force: bool = False,
) -> None:
    """Extracts decontaminated signals from ROIs.

    Note that 'source' can be either a single file or a directory. If it is a directory,
    all the HDF5 files it contains will be converted.

    By default, all provided files are treated as separate sessions. In order to process
    files together, use 'group_by_regex' to group paths together based on a regular
    expression. If you wish to group all files together, pass an empty string as the
    regular expression.

    Args:
        source (pathlib.Path):
            Source file or directory to preprocess. If a directory, the default is to
            look for HDF5 files inside of it without recursion.
        group_by_regex (str, optional):
            Regular expression to use when grouping sources together. This results in
            the paths being preprocessed together based on the regex. This is ignored if
            source is a single file. Note that using this can lead to a very high memory
            usage depending on how many chunks needs to be loaded. Also note that for
            grouping to work, grouped files should have the same number of ROIs
        dataset_name (str, optional):
            Name of the HDF5 dataset to work with.
        recursive (bool, optional):
            Whether to search directories recursively when looking for HDF5 files.
        include (str | None, optional):
            Include filters to apply when searching for HDF5 files. This supports
            regular-expressions. Include filters are applied before any exclude filters.
        exclude (str | None, optional):
            Exclude filters to apply when searching for HDF5 files. This supports
            regular-expressions. Exclude filters are applied after all include filters.
        dont_abort_on_skipped_file (bool, optional):
            Whether to keep working on a group if one or more of its paths is skipped
            for any reason (e.g., file was already preprocessed by '--force' is not
            set).
        force (bool, optional): Whether to overwrite output files if they exist.
    """
    paths = io.find_paths(source, [".h5"], include, exclude, recursive, True)
    groups = [[path] for path in paths]
    if group_by_regex is not None:
        groups = io.group_paths_by_regex(paths, group_by_regex)

    for group in groups:
        _extract_signal_for_group(
            group, dataset_name, dont_abort_on_skipped_file, force
        )


def _extract_signal_for_group(
    group: list[pathlib.Path],
    dataset_name: str,
    dont_abort_on_skipped_file: bool,
    force: bool,
) -> None:
    # Lazy time-consuming import
    import fissa

    handles: list[h5py.File] = []

    def abort() -> None:
        for handle in handles:
            handle.close()

    _logger.info(
        f"Extracting and decontaminating signal for "
        f"'{", '".join(x.stem for x in group)}'."
    )

    skip_or_abort_message = (
        " Skipping file."
        if dont_abort_on_skipped_file
        else " Aborting preprocessing of group."
    )

    datasets = []
    all_rois = []
    for path in group:
        _logger.debug(f"Opening handle for '{path}'.")

        handle = h5py.File(path, "a", locking=False)

        # Extract the motion corrected dataset
        dataset = handle.get(dataset_name)
        if dataset is None:
            _logger.error(
                f"Could not find group '{dataset_name}' in file '{path}'. "
                f"Available groups are: {list(handle)}."
                f"{skip_or_abort_message}"
            )
            if dont_abort_on_skipped_file:
                handle.close()
                continue

            abort()
            return

        # Check for existing signal extraction
        if handle.get("extracted") and not force:
            _logger.info(
                f"Extracted group already exists in '{path}' and 'force' was "
                f"not set. "
                f"{skip_or_abort_message}"
            )
            if dont_abort_on_skipped_file:
                handle.close()
                continue

            abort()
            return

        # Read ROIs
        rois, _ = io.read_rois_and_shapes(handle)
        if not rois:
            _logger.error(f"Could not find ROIs in '{path}'.{skip_or_abort_message}")
            if dont_abort_on_skipped_file:
                handle.close()
                continue

            abort()
            return

        handles.append(handle)
        datasets.append(dataset)
        all_rois.append(rois)

    if len(handles) == 0:
        _logger.error("All files for the current group were skipped.")
        return

    experiment = fissa.Experiment(datasets, all_rois)
    # This adds a .result array to experiment which has shape:
    # (ROI, trial)(signal, timepoint)  # noqa: ERA001
    # where:
    #     ROI is the ROI index,
    #     trial is the dataset index
    #     signal is the signal index (0 is strongest)
    #     timepoint is the frame index
    experiment.separate()

    for trial_index, handle in enumerate(handles):
        # Ensure group doesn't exist
        if handle.get("extracted") is not None:
            _logger.debug("Deleting exisintg preprocessing.")
            del handle["extracted"]

        _logger.debug("Saving results.")
        extracted_group = handle.create_group("extracted")
        for roi_index in range(experiment.result.shape[0]):
            extracted_group.create_dataset(
                f"roi{roi_index}", data=experiment.result[roi_index, trial_index]
            )

    _logger.info("Finished extracting signal.")
