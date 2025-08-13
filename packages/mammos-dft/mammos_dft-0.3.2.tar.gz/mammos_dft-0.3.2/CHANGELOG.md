# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This project uses [towncrier](https://towncrier.readthedocs.io/) and the changes for the upcoming release can be found in [changes](changes).

<!-- towncrier release notes start -->

## [mammos-dft 0.3.2](https://github.com/MaMMoS-project/mammos-dft/tree/0.3.2) – 2025-08-13

### Fixed

- Update attribute name of uniaxial anisotropy constant to `Ku_0` from `K1_0` for the returned `MicromagneticProperties` object during a database lookup. ([#19](https://github.com/MaMMoS-project/mammos-dft/pull/19))

### Misc

- Use [towncrier](https://towncrier.readthedocs.io) to generate changelog from fragments. Each new PR must include a changelog fragment. ([#20](https://github.com/MaMMoS-project/mammos-dft/pull/20))
