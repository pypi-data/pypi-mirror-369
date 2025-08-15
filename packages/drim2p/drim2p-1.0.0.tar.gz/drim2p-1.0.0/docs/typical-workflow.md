A typical workflow involves the following steps:

1. [Conversion from RAW to HDF5](#conversion-from-raw-to-hdf5)
1. [Motion correction](#motion-correction)
1. [ROI drawing](#roi-drawing)
1. [Signal extraction and decontamination](#signal-extraction-and-decontamination)
1. [ΔF/F₀ computation](#ff0-computation)

This provides a very broad overview of what the software provides. For a step-by-step guide going through each of these commands, you should read the [tutorials](tutorials/index.md).

## Conversion from RAW to HDF5

This step converts the RAW binary files coming from a 2-photon scope into the HDF5 file format for easier storage.

[Command](reference/index.md#drim2p-convert-raw):

```shell
drim2p convert raw /path/to/your/recordings.raw
```

## Motion correction

This step corrects for motion artifacts in recordings.

[Command](reference/index.md#drim2p-motion-correct):

```shell
drim2p motion correct /path/to/your/recordings.h5 --settings-path /path/to/your/settings.toml
```

## ROI drawing

This step allows drawing ROIs around cells for further preprocessing.

[Command](reference/index.md#drim2p-draw-roi):

```shell
drim2p draw roi /path/to/your/recordings.h5
```

## Signal extraction and decontamination

This step extracts "true" signals for the cells denoted by the drawn ROIs.

[Command](reference/index.md#drim2p-extract-signal):

```shell
drim2p extract signal /path/to/your/recordings.h5
```

## ΔF/F₀ computation

This step compute ΔF/F₀ for extracted signals.

[Command](reference/index.md#drim2p-deltaf):

```shell
drim2p delta /path/to/your/recordings.h
```
