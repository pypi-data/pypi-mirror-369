The first step when working with RAW data is to convert it to a file format that allows shaping it correctly and appending metadata about its datatype, acquisition, etc. `drim2p` uses the [HDF5](https://en.wikipedia.org/wiki/Hierarchical_Data_Format) file format.

## Converting

With a terminal open in the directory with your files, simply run:

```shell
drim2p convert raw .
```

!!! note
    For many of the commands in these tutorials, you will see a `.` after the name of the command or subcommand. This is used to denote the current working directory and is used by `drim2p` to find the file it should process. If you are working from outside the directory where your files are located, simply replace the `.` with the absolute or relative path to the relevant folder.

If all goes well, you will see some output along these lines:

```text
Converting 'imaging_file.raw'.
Finished converting 'imaging_file.raw'.
```

And your directory will now contain an extra `.h5` file:

```shell
tutorial/
├── imaging_file.h5  (NEW)
├── imaging_file.ini
├── imaging_file.raw
└── imaging_file.xml
```

If you see a warning but no error, you file should still be converted properly, but some metadata might not be conserved.  

If you see an error, then something prevented the conversion from going ahead. The most common error looks like this:

```text
Failed to retrieve OME-XML metadata from INI file or directly through XML file. 
```

If you get this error, you should ensure you have the proper file structure as described in the [overview](index.md#prerequisites) then try again.

If you get a different error, you should read the message to try and understand what went wrong. If you are not sure how to solve it, try looking for the error message on the [issues page](https://github.com/DuguidLab/drim2p/issues?q=is%3Aissue).

!!! note
    Since this is the first step, and to get you on the right track, this tutorial tries to cover cases where the command does not run properly. Future tutorials will only present what the expected output is. If you run into issues in those tutorials, follow the instructions detailed above and have a look at the issues.

## What's next?

You are now ready to preprocess your data. To begin, move on to [motion correction](motion-correction.md).
