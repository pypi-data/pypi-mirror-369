This tutorial series will guide through step-by-step instructions on how to use `drim2p` as a command-line tool. Tutorials will show you how to prepare you data, motion correct it, draw ROIs, extract and decontaminate signals, and compute ΔF/F₀.

## Prerequisites

Before you start, you should have a 2-photon imaging file you wish to preprocess in the RAW binary format (i.e., uses the `.raw` extension). A small one, ideally under 250 MiB, will work best so you don't have to wait for it to be preprocessed between steps and you can easily run it on your own machine. Although small, you should expect to be able to discern individual cells when the image is maximum-projected for ROI drawing.
Alongside this file, you should have an INI file with OME-XML metadata (failing that, you should have a standalone OME-XML metadata file).

This INI file can contain any arbitrary metadata (but only a single section) about your RAW file which will be attached as attributes when converting to HDF5. No entry is mandatory but if you do not have a separate OME-XML file, your INI file will need to have an `ome.xml.string` entry that contains a valid OME-XML string with information about your file. This is required because the RAW file format does not contain any information about the data it stores and the OME-XML metadata is what is used to read and reshape the RAW file properly.

An example directory with the required files looks like this:

```shell
tutorial/
├── imaging_file.ini
├── imaging_file.raw
└── imaging_file.xml
```

## What's next?

When you have all the required files in a directory and you have a terminal open in that directory, you should move on to [convertion to HDF5](conversion-to-hdf5.md).
