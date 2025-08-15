ΔF/F₀ is a normalisation technique that enables comparing signal values between recordings as well as between cells in the same recording.

There are multiple ways to compute F₀, using a percentile, the mean, the median, etc. By default, `drim2p` computes F₀ to be the 5th percentile of the fluorescence for the whole signal.

It is also possible to use a rolling window to continually update the F₀ value throughout the signal.

This tutorial focuses on the using the defaults (5th percentile with no rolling window). For a more in-depth guide to customising the computation, see the [how-to guide]() and the [CLI reference](../reference/index.md#drim2p-deltaf).

## Calculating ΔF/F₀

To compute ΔF/F₀, simply run:

```shell
drim2p deltaf .
```

If all goes well, you will see output along these lines (the computation should be very fast for any size of recording):

```text
Computing ΔF/F₀ for 'imaging_file.h5'.
Saved ΔF/F₀.
```

## What's next?

This is the final tutorial guiding you through the `drim2p` pipeline. Now that you have ΔF/F₀ traces, you can carry out custom analysis and plotting, or optionally, you can use the provided template for spike inference as described in the [how-to]() guide.
