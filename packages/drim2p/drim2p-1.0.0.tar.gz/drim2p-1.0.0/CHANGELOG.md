# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

-

## [1.0.0] - 2025-08-15

### Added

- The package is now available for download from PyPI as a 1.0.0 release.

## [0.7.0] - 2025-08-13

### Added

- Switch to using `uv` for package management and add linting ([#37](https://github.com/DuguidLab/drim2p/pull/37)).

### Fixed

- Fix various CLI bugs ([#38](https://github.com/DuguidLab/drim2p/pull/38)).

### Changed

- Change GUI maximum intensity projection to average intensity projection ([#40](https://github.com/DuguidLab/drim2p/pull/40)).

## [0.6.0] - 2025-07-14

### Added

- Add documentation skeleton ([#34](https://github.com/DuguidLab/drim2p/pull/34)).
- Flesh out tutorial docs ([#35](https://github.com/DuguidLab/drim2p/pull/35)).

### Changed

- Make a bunch of small improvements ([#36](https://github.com/DuguidLab/drim2p/pull/36)).

## [0.5.0] - 2025-07-08

### Added

- Add ΔF/F₀ command ([#21](https://github.com/DuguidLab/drim2p/pull/21)).

## [0.4.0] - 2025-07-08

### Added

- Add signal extraction and decontamination ([#19](https://github.com/DuguidLab/drim2p/pull/19)).

## [0.3.0] - 2025-07-07

### Added

- Add ROI drawing GUI ([#15](https://github.com/DuguidLab/drim2p/pull/15)).

### Fixed

- Ensure SIMA cache doesn't exist before starting ([#19](https://github.com/DuguidLab/drim2p/pull/19)).

### Changed

- Delay import of `ome_types` ([#16](https://github.com/DuguidLab/drim2p/pull/16)).
- Improve motion correction performance ([#17](https://github.com/DuguidLab/drim2p/pull/17)).

## [0.2.0] - 2025-06-17

### Added

- Add motion correction with SIMA ([#13](https://github.com/DuguidLab/drim2p/pull/13)).

### Changed

- Split mypy report into its own command ([#14](https://github.com/DuguidLab/drim2p/pull/14)).

## [0.1.0] - 2025-06-10

### Added

- Add RAW to HDF5 converter ([#7](https://github.com/DuguidLab/drim2p/pull/7)).
- Add changelog ([#8](https://github.com/DuguidLab/drim2p/pull/8)).

## [0.0.1] - 2025-05-26

### Added

- Set up project skeleton and update basic metadata ([#5](https://github.com/DuguidLab/drim2p/pull/5)).
- Add mypy configuration ([#6](https://github.com/DuguidLab/drim2p/pull/6)).
