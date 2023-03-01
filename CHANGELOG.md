# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Removed
- Drop support for 3.6

## [2.0.1] - 2023-02-22
### Changed
- Configure optional dependency groups for development dependencies. Requires fewer dependencies to be installed when installing the package.
- Improved the documentation

### Added - 2023-02-28
- Added smile-Id constants
- Added custom types
- Added Business verification
- Added runnable examples for products
- Increased test coverage to 99%

### Fixed
- Resolved image-upload bug in handling image types

## [2.0.0] - 2022-11-25
### Added
- Add coverage reports.
- Added github action to release the package.

### Changed
- improved the documentation.
- Added types to IdApi, ServerError, Utilities, and WebApi classes.
- Renamed WebApi get_job_status param from sec_params to signature_params
- Renamed WebApi poll_job_status param from sec_params to signature_params

### Removed
- Remove sec key

## [1.0.9] - 2022-11-01
### Added
- Python 3.11 support.
- Package version now available via `__version__` attribute.

### Changed
- Project is now built with [Poetry](https://python-poetry.org).
- Moved information of python version to the class initialization.
- Lint codebase using black.

## [1.0.8] - 2022-04-26
### Fixed
- Fixed a bug with optional `job_type` parameter for job status endpoint.

## [1.0.7] - 2022-04-26
### Changed
- Do not require `job_type` to be set for job status endpoint.

## [1.0.6] - 2022-04-25
### Added
- Added support for image files ending with `.jpeg`.

### Changed
- make `return_images` and `return_history` optional arguments for job status endpoint.

## [1.0.5] - 2022-02-28
### Added
- Added support for Document Verification job type.

## [1.0.4] - 2022-02-07
## [1.0.3] - 2021-11-10
## [1.0.2] - 2021-11-02
## [1.0.1] - 2021-10-04
## [1.0.0] - 2021-09-13

## [0.0.13] - 2020-09-16
### Added
- Created changelog.
- Fixed job status error string format.
- Added black for code formatting.
- Fixed python semantics.
- Moved zipfile out from webapi class.

## [0.0.12] - 2022-08-19
