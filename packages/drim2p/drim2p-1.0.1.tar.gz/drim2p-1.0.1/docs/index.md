# Getting started

[`drim2p`](https://github.com/DuguidLab/drim2p) is an open-source package that facilitates the preprocessing of 2-photon calcium imaging recordings through a unified pipeline.

## Prerequisites

`drim2p` is programmed in Python and you will need to have it installed on your machine. On all major platforms, it will be installed by default. But if you do not have it, follow the instructions available [here](https://www.python.org/downloads/).

`drim2p` takes as input `.raw` files outputted from a 2-photon imaging scope (e.g., Hyperscope). This is essentially all you will need to run the whole pipeline, except for a `settings.toml` file that is used for motion correction. You can find this extra file under `resources/motion_correction` in the repository.

No specific preprocessing is necessary in order to use the software. However, since `.raw` files are in fact raw binary, some metadata is required for the software to be able to read the files. This metadata can take the form of an `.ini` file or an `.ome.xml` file. If an `.ini` file is present, it needs to have an `ome.xml.string` entry which contains a valid OME-XML string.

For more details, see the [tutorials overview](tutorials/index.md) and the [tutorial on conversion](tutorials/conversion-to-hdf5.md).

## Installation as a command

`drim2p` is being developed with mostly Linux in mind. It is expected that most functionality should be available on macOS, but Windows support is not guaranteed. Instead, users should opt to use the [Windows Subsystem for Linux](https://en.wikipedia.org/wiki/Windows_Subsystem_for_Linux) available on Windows 10 and newer.

If you run into troubles when trying to install `pipx`, refer to the latest documentation from [their website](https://pipx.pypa.io/latest/installation/#installing-pipx) to see if it fixes the problem. If you run into troubles when trying to install `drim2p` itself, have a read through the [open and closed issues](https://github.com/DuguidLab/drim2p/issues?q=is%3Aissue) on the package's GitHub. If you do not find an answer after looking through those, feel free to [open a new one](https://github.com/DuguidLab/drim2p/issues/new), detailing your problem as best you can.

### Installing `pipx`

#### On Linux

##### Ubuntu 23.04 or above

```shell
sudo apt update
sudo apt install pipx
pipx ensurepath
```

##### Fedora

```shell
sudo dnf install pipx
pipx ensurepath
```

##### Other distributions (using `pip`)

```shell
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

#### On macOS

```shell
brew install pipx
pipx ensurepath
```

#### On Windows

On Windows, the recommended way to run `drim2p` is using the [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install) (WSL). If you do not have it enabled and do not wish to do so, you can follow the rest of these instructions. If you wish to continue with WSL, install `pipx` using the [Linux instructions](#on-linux) above.
The recommended way to install `pipx` on Windows is using [Scoop](https://scoop.sh/). Once Scoop is installed, run the following commands.

```shell
scoop install pipx
pipx ensurepath
```

However, you can also install it using `pip`:

```shell
python3 -m pip install --user pipx
```

### Installing `drim2p`

Once `pipx` has been installed, run the following command:i

```shell
pip install drim2p
```

And that should be you sorted! From there, `drim2p` will be available as a command in your terminal.

To ensure that everything installed property, you can run:

```
drim2p --help
```

If you see usage information printed out, all went well. If you see something telling you that `drim2p` is not a recognised command, ensure you have followed all the previous steps properly. If you are still having problem after that, consult the [issues page](https://github.com/DuguidLab/drim2p/issues?q=is%3Aissue) on the package's GitHub.

## Installation as a library

Most users will only need the command-line version of `drim2p`, but users willing to use its API in their own scripts can install it as a library.

To do so, clone the repository locally:

```shell
git clone https://github.com/DuguidLab/drim2p
```

Navigate into the cloned directory:

```shell
cd drim2p
```

And install it in the Python environment you wish to use:

```shell
pip install .
```


## What's next?

For your first time working with the app, you should start by reading the [typical workflow](typical-workflow.md) to get an overview of what you can do with the app.

For more in-depth guides once you've got a good grip on the main capabilities of the application, see the [tutorials](tutorials/index.md) which guide you through the commands and in-depth explanations of what each step entails.

For documentation of the `drim2p` API to use in your own project, see the [reference](reference/API/drim2p/index.html) section.
