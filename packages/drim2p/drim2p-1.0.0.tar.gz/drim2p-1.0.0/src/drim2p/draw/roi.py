# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import contextlib
import logging
import pathlib
from typing import Any

import click
import dask.array as da
import h5py
import napari
import numpy as np

from drim2p import cli_utils
from drim2p import io

_logger = logging.getLogger(__name__)


@click.command("roi")
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
    "-t",
    "--template",
    required=False,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path
    ),
    default=None,
    help=(
        "Path to the HDF5 file to read default ROIs from. When provided, any ROIs "
        "already present in the file will be used as the default ROIs for all SOURCE "
        "file. Use in conjunction with '--force' to overwrite any existing ROIs with "
        "the template ones."
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
    "-w",
    "--projection-window",
    required=False,
    type=click.INT,
    default=10,
    help="Window size to use for grouped Z projections.",
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
    "--lazy",
    required=False,
    is_flag=True,
    help=(
        "Whether to lazily load the file. This will speed up the GUI startup time but "
        "will slow down any slicing when it is open. This will also disable the"
        "mean intensity projection."
    ),
)
@click.option(
    "--force",
    required=False,
    is_flag=True,
    help=(
        "Whether to ovewrite ROIs if some are found in SOURCE. "
        "Otherwise, ROIs are appended. Be careful when using this option as it will "
        "lead to all ROIs being deleted when opening a file."
    ),
)
def draw_roi_command(**kwargs: Any) -> None:
    """Starts a napari GUI to draw ROIs on HDF5 datasets.

    Note that SOURCE can be either a single file or a directory. If it is a directory,
    all the HDF5 files it contains will be queued for ROI drawing.
    """
    draw_roi(**kwargs)


def draw_roi(
    source: pathlib.Path,
    template: pathlib.Path | None = None,
    dataset_name: str = "imaging",
    projection_window: int = 10,
    recursive: bool = False,
    include: str | None = None,
    exclude: str | None = None,
    lazy: bool = False,
    force: bool = False,
) -> None:
    """Starts a napari GUI to draw ROIs on HDF5 datasets.

    Note that SOURCE can be either a single file or a directory. If it is a directory,
    all the HDF5 files it contains will be queued for ROI drawing.

    Args:
        source (pathlib.Path):
            Source file or directory to convert. If a directory, the default is to look
            for HDF5 files inside of it without recursion.
        template (pathlib.Path | None, optional):
            Path to the HDF5 file to read default ROIs from. When provided, any ROIs
            already present in the file will be used as the default ROIs for all source
            file. Use in conjunction with 'force' to overwrite any existing ROIs with
            the template ones.
        dataset_name (str, optional):
            Name of the HDF5 dataset to display for ROI drawing.
        projection_window (int, optional): Window size to use for grouped Z projections.
        recursive (bool, optional):
            Whether to search directories recursively when looking for HDF5 files.
        include (str | None, optional):
            Include filters to apply when searching for HDF5 files. This supports
            regular-expressions. Include filters are applied before any exclude filters.
        exclude (str | None, optional):
            Exclude filters to apply when searching for HDF5 files. This supports
            regular-expressions. Exclude filters are applied after all include filters.
        lazy (bool, optional):
            Whether to lazily load the file. This will speed up the GUI startup time
            but will slow down any slicing when it is open. This will also disable the
            mean intensity projection.
        force (bool, optional):
            Whether to ovewrite ROIs if some are found in source. Otheriwse, ROIs are
            appended. Be careful when using this option as it will lead to all ROIs
            being deleted when opening a file.
    """
    # Load template ROIs
    template_rois: list[np.ndarray[Any, np.dtype[np.number]]] = []
    template_roi_shape_types: list[str] = []
    if template is not None:
        with h5py.File(template) as handle:
            _logger.debug("Loading ROIs from template.")
            template_rois, template_roi_shape_types = io.read_rois_and_shapes(handle)

            if not template_rois:
                # Stop early if the template is empty since this most likely means the
                # user used the wrong option/file. We could also only abort when force
                # is set.
                _logger.error(
                    f"Could not load ROIs from provided template '{template}'. "
                    f"Either there weren't any ROIs or the file structure was "
                    f"unexpected. Ensure you have provided the correct template and "
                    f"try again."
                )
                return

    for path in io.find_paths(source, [".h5"], include, exclude, recursive, True):
        _logger.info(f"Opening '{path}'.")
        with h5py.File(path) as handle:
            # Load the motion-corrected dataset
            dataset = handle.get(dataset_name)
            if dataset is None:
                _logger.error(
                    f"Could not find group '{dataset_name}' in file '{path}'."
                    f"Available groups are: {list(handle)}. Skipping file."
                )
                continue

            # Convert to a Dask array so we can optionally, lazily load the array
            array: da.Array = da.from_array(
                dataset, chunks=(projection_window, *dataset.shape[1:])
            )
            # Make mean intensity grouped projections every projection_window frames
            grouped: da.Array = array.map_blocks(
                lambda x: da.mean(x, axis=0, keepdims=True),  # type: ignore[arg-type]
                chunks=(1, *dataset.shape[1:]),
            )  # type: ignore[call-arg]

            # Make complete projection
            projected: da.Array | None = None
            if not lazy:
                _logger.debug("Persisting arrays into memory.")
                array = array.persist()
                # Redefining grouped is about twice a fast as simply persisting it if
                # array was also persisted before it. Not exactly sure why.
                grouped = array.map_blocks(
                    lambda x: da.mean(x, axis=0, keepdims=True),  # type: ignore[arg-type]
                    chunks=(1, *dataset.shape[1:]),
                ).persist()  # type: ignore[call-arg]
                # We could look for a pre-computed QA projection but we're loading the
                # whole array into memory anyway so processing is pretty short.
                projected = da.mean(grouped, axis=0).persist()

            # Retrieve ROIs if they exist
            rois: list[np.ndarray[Any, np.dtype[np.number]]] = []
            roi_shape_types: list[str] = []
            if not force:
                rois, roi_shape_types = io.read_rois_and_shapes(handle)
            else:
                _logger.debug("'force' was set. Skipping looking for existing ROIs.")

            # Merge template and existing
            rois += template_rois
            roi_shape_types += template_roi_shape_types

            # If a template is used on a file twice or more, it will generate
            # duplicates.
            rois, roi_shape_types = _remove_duplicates(rois, roi_shape_types)

            # Update ROIs with modifications from GUI
            rois = _start_roi_gui(grouped, projected, rois, roi_shape_types)

            # ROI layer was deleted before GUI was closed, don't overwrite
            if not rois:
                _logger.debug(
                    f"'ROIs' layer was deleted. Skipping writing for '{path}'."
                )
                continue

        with h5py.File(path, "a") as handle:
            # Use this opportunity to save the mean projection for QA if we computed it
            if projected is not None:
                qa_group = handle.get("QA/projections/motion_corrected")
                if qa_group is None:
                    qa_group = handle.create_group("QA/projections/motion_corrected")

                with contextlib.suppress(KeyError):
                    del qa_group["mean_intensity_projection"]

                _logger.debug("Saving mean projection.")
                qa_group.create_dataset("mean_intensity_projection", data=projected)

            # Add all ROIs to file. If force is not set, the ROIs will have already been
            # retrieved above so we can just delete them in the file and re-add them
            # with the new ones.
            if handle.get("ROIs") is not None:
                _logger.debug("Deleting exisintg ROIs.")
                del handle["ROIs"]

            _logger.debug("Saving ROIs.")
            roi_group = handle.create_group("ROIs")
            roi_shape_types = []
            for index, (roi, shape_type) in enumerate(
                zip(rois.data, rois.shape_type, strict=True)
            ):
                # Discard line and path ROIs
                if shape_type not in {"rectangle", "ellipse", "polygon"}:
                    _logger.error(
                        f"ROI {index} has an unssuported shape type '{shape_type}'. "
                        f"Discarding it."
                    )
                    continue

                roi_group.create_dataset(f"roi{index}", data=roi)
                roi_shape_types.append(shape_type)

            # Save ROI types
            roi_group.create_dataset("roi_shape_types", data=rois.shape_type)


def _start_roi_gui(
    grouped: da.Array,
    projected: da.Array | None = None,
    rois: list[np.ndarray[Any, np.dtype[np.number]]] | None = None,
    roi_shape_types: str | list[str] | None = None,
) -> napari.layers.shapes.shapes.Shapes | None:
    if roi_shape_types is None:
        roi_shape_types = "rectangle"

    _logger.debug("Preparing napari viewer.")
    viewer = napari.viewer.Viewer(show=False)

    # Add 2D (YX) mean projection if provided. It can be missing if we are lazily
    # loading the data.
    if projected is not None:
        viewer.add_image(
            da.squeeze(projected),  # Ensure we only have YX
            name="Mean intensity projection",
        )

    # Add 3D (TYX) grouped Z projections
    viewer.add_image(
        da.squeeze(grouped),  # Ensure we only have TYX
        name="Grouped Z projections",
        visible=projected is None,
    )
    viewer.dims.current_step = (0, *viewer.dims.current_step[1:])  # Start at index 0

    # Add ROIs
    viewer.add_shapes(
        data=rois,
        name="ROIs",
        ndim=2,  # Necessary to have ROIs apply across all slices
        shape_type=roi_shape_types,
        # Opaque magenta, other basic colours are hard to see on hover
        edge_color="#FF00FFFF",
        # Fully transparent
        face_color="#00000000",
    )

    _logger.debug("Starting napari GUI.")
    viewer.show()
    napari.run()

    # Retrieve ROIs from a layer named 'ROIs'
    shapes_layers = [layer for layer in viewer.layers if layer.name == "ROIs"]
    if len(shapes_layers) < 1:
        shapes_layer = []
    elif len(shapes_layers) > 1:
        _logger.warning("Found multiple ROI layers. Using the first one.")
        shapes_layer = shapes_layers[0]
    else:
        shapes_layer = shapes_layers[0]

    return shapes_layer


def _remove_duplicates(
    rois: list[np.ndarray[Any, np.dtype[np.number]]],
    roi_shape_types: list[str],
) -> tuple[list[np.ndarray[Any, np.dtype[np.number]]], list[str]]:
    # If we have fewer than 2 ROIs, return early
    if len(rois) < 2:  # noqa: PLR2004
        return rois, roi_shape_types

    i = 1
    while i < len(rois):
        current = rois[i]
        # Check if current ROI is a duplicate of any of the previous ones
        if any(
            np.all(current == roi) for roi in rois[:i] if current.shape == roi.shape
        ):
            rois.pop(i)
            roi_shape_types.pop(i)
            continue

        i += 1

    return rois, roi_shape_types
