# Pigreads

[![Pipeline Status][pipeline-badge]][pipeline-link]
[![Coverage Report][coverage-badge]][coverage-link]
[![Documentation Status][rtd-badge]][rtd-link]

[![Latest Release][release-badge]][release-link]
[![PyPI platforms][pypi-platforms]][pypi-link]
[![PyPI version][pypi-version]][pypi-link]

<!-- SPHINX-START -->

Pigreads stands for **Python-integrated GPU-enabled reaction diffusion solver**.

## Getting started

### Requirements

Pigreads uses OpenCL for calculations on the graphics cards. OpenCL is usually
included in the drivers for your graphics card. The following pages may help
installing and accessing OpenCL:

- [ArchWiki: OpenCL on Arch Linux][guide-arch]
- [OpenCL-Guide: OpenCL on Ubuntu Linux][guide-ubuntu]
- [OpenCL-Guide: OpenCL on Windows][guide-windows]

You can use [`clinfo`][clinfo] to verify you have an OpenCL platform installed.

If instead of the GPU, you want to use CPUs, you can [install PoCL][pocl] as an
OpenCL platform to compute on the main processors.

To compile and use the module, you may also need to install the following tools:

- [Python][python] with the `pip` package manager
- [CMake][cmake]
- [GNU Make][make]
- [GNU C++ compiler][gcc]

### Installation

Install this Python package in the standard way using `pip`, for instance from
[PyPI][pypi-link] or from a local copy of this repository, see [the Python
documentation for details][py-install]. For the command line interface (CLI),
also install the optional dependency `cli`:

```
$ pip install pigreads[cli] # from PyPI
$ pip install .[cli] # from current directory
```

### Usage

Simulations can be performed via calls to the Python module (API) or using the
CLI. See the API and CLI sections in the [documentation for annotated
examples][rtd-link], or the examples directory in the [Pigreads
repository][repo].

<!-- prettier-ignore-start -->
[repo]:           https://gitlab.com/pigreads/pigreads
[coverage-badge]: https://gitlab.com/pigreads/pigreads/badges/main/coverage.svg
[coverage-link]:  https://gitlab.com/pigreads/pigreads/-/commits/main
[pipeline-badge]: https://gitlab.com/pigreads/pigreads/badges/main/pipeline.svg
[pipeline-link]:  https://gitlab.com/pigreads/pigreads/-/pipelines
[pypi-link]:      https://pypi.org/project/pigreads/
[pypi-platforms]: https://img.shields.io/pypi/pyversions/pigreads
[pypi-version]:   https://img.shields.io/pypi/v/pigreads
[release-badge]:  https://gitlab.com/pigreads/pigreads/-/badges/release.svg
[release-link]:   https://gitlab.com/pigreads/pigreads/-/releases
[rtd-badge]:      https://readthedocs.org/projects/pigreads/badge/?version=latest
[rtd-link]:       https://pigreads.readthedocs.io/en/latest/?badge=latest
[python]:         https://www.python.org/
[py-install]:     https://packaging.python.org/en/latest/tutorials/installing-packages/
[guide-arch]:     https://wiki.archlinux.org/title/OpenCL
[guide-ubuntu]:   https://github.com/KhronosGroup/OpenCL-Guide/blob/main/chapters/getting_started_linux.md
[guide-windows]:  https://github.com/KhronosGroup/OpenCL-Guide/blob/main/chapters/getting_started_windows.md
[clinfo]:         https://github.com/Oblomov/clinfo
[pocl]:           https://portablecl.org/docs/html/install.html
[gcc]:            https://gcc.gnu.org/
[make]:           https://www.gnu.org/software/make/
[cmake]:          https://cmake.org/
<!-- prettier-ignore-end -->
