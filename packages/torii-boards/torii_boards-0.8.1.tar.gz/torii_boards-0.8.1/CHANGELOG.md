<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
Unreleased template stuff

## [Unreleased]
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
-->

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

## [0.8.1] - 2025-08-13

> [!IMPORTANT]
> The minimum Python version for Torii and Torii Boards is now 3.11

### Changed

- Switched from using the old setuptools `setup.py` over to setuptools via `pyproject.toml`
- Board files have been categorized into their FPGA sub-families.
  - `torii_boards.altera` now has `cyclone_iii`, `cyclone_iv`, `cyclone_v`, and `max10` submodules.
  - `torii_boards.gowin` now has a `gw1n` submodule.
  - `torii_boards.lattice` now has `ecp5`, `ice40`, `machxo2`, and `machxo3` submodules.
  - `torii_boards.quicklogic` now has a `eos_3s` submodule.
  - `torii_boards.xilinx` now has `artix7`, `kintex_us`, `kintex7`, `spartan3`, `spartan6`, `spartan7`, and `zynq7` submodules.

### Deprecated

- Board imports from the root FPGA namespace have been deprecated in favor of using the sub-family name.

### Fixed

- All board files now use the appropriate Torii platform resources where possible.

## [0.8.0] - 2025-06-26

This is a maintenance release, syncs the minimum [Torii] version to `0.8.0` in preparation for
the Torii `v1.0.0` release in the future.

## [0.7.5] - 2025-03-07

### Changed

- Bumped the minimum version of Torii to be 0.7.5

### Removed

- Removed the deprecated `torii_boards.intel` module.

## [0.6.1] - 2024-09-10

### Fixed

- Fixed the platform import in `torii_boards.lattice.tinyfpga_ax1` and `torii_boards.lattice.tinyfpga_ax2`, as they still used the old Lattice MachXO2 platform name

## [0.6.0] - 2024-05-06

### Changed

- Bumped the minium version of Python to match with Torii 0.6.0
- Bumped the minimum version of Torii to be 0.6.0

### Deprecated

- Deprecated the `torii_boards.intel` boards in favor of `torii_boards.altera`, following the `IntelPlatform` deprecation in Torii 0.6.0

### Fixed

- Fixed the Gowin boards title in the docs

## [0.5.0] - 2023-10-23

### Added

- Added the `cmod_a7` and `cmod_s7` Xilinx FPGA boards from digilent.
- Added the `Upduino v3` Lattice FPGA board from TinyVision.
- Added the `Tang Nano` Gowin FPGA board from sipeed.
- Added the LEFUM5-85F variant of the orangecrab FPGA board.

### Fixed

- Fixed SRAM ~CE pin assignment in the blackice_ii board.
- Fixed IO direction for  the i2c clock lines on the mister and de10-nano

## [0.4.1] - 2023-02-27

### Fixed

- Fixed the import in the Xilinx ArtyS7 and Atlys board files where they were using the improper import in `toolchain_program` for `required_tool`.

## [0.4.0] - 2022-12-02

### Added

- Added [Code of Conduct](https://github.com/shrine-maiden-heavy-industries/torii-boards/blob/main/CODE_OF_CONDUCT.md)
- Added [flake8](https://flake8.pycqa.org/en/latest/) configuration file.
- Added [mypy](https://mypy-lang.org/) configuration file.
- Added a `noxfile.py` for use with [nox](https://nox.thea.codes/en/stable/).
- Added `MEGA65` board definitions file [#1](https://github.com/shrine-maiden-heavy-industries/torii-boards/pull/1)

### Changed

- Renamed from `amaranth_boards` to `torii_boards`
- Updated the CI scripts.
- Moved Intel based platforms into `torii_boards.intel`.
- Moved Xilinx based platforms into `torii_boards.xilinx`.
- Moved Lattice based platforms into `torii_boards.lattice`.
- Moved Quicklogic based platforms into `torii_boards.quicklogic`.
- Moved the `torii_boards.extensions` into `torii_boards.resources.extensions`.

### Removed

- Removed the `nMigen` compatibility layer.
- Removed the `torii_boards.resources` and migrated that to [`torii.platform.resources`](https://github.com/shrine-maiden-heavy-industries/torii-hdl/tree/main/torii/platform/resources)

### Fixed

- Fixed the package name.
- Fixed the package authors.
- Fixed the package trove classifiers.
- Fixed all flake8 warnings on the entire codebase.
- Fixed indentation.

## [0.1.0] - [0.3.0]

No changelog is provided for these versions as they are all older untagged releases of [Amaranth Boards](https://github.com/amaranth-lang/amaranth-boards) from before the fork.

[unreleased]: https://github.com/shrine-maiden-heavy-industries/torii-boards/compare/v0.8.1...main
[0.8.1]: https://github.com/shrine-maiden-heavy-industries/torii-boards/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/shrine-maiden-heavy-industries/torii-boards/compare/v0.7.5...v0.8.0
[0.7.5]: https://github.com/shrine-maiden-heavy-industries/torii-boards/compare/v0.6.1...v0.7.5
[0.6.1]: https://github.com/shrine-maiden-heavy-industries/torii-boards/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/shrine-maiden-heavy-industries/torii-boards/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/shrine-maiden-heavy-industries/torii-boards/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/shrine-maiden-heavy-industries/torii-boards/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/shrine-maiden-heavy-industries/torii-boards/compare/amaranth-fork...v0.4.0
[0.3.0]: https://github.com/shrine-maiden-heavy-industries/torii-boards/compare/amaranth-fork...main
[0.1.0]: https://github.com/shrine-maiden-heavy-industries/torii-boards/compare/amaranth-fork...main
[Torii]: https://github.com/shrine-maiden-heavy-industries/torii-hdl
