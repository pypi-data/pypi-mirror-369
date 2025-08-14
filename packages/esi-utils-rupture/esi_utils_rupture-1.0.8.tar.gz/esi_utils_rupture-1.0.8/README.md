# esi-utils-rupture

## Introduction

Utility package with some helper functions for representing ruptures and computing
rupture distances used by USGS earthquake hazard products such as ShakeMap and gmprocess.

See tests directory for usage examples.

## Installation

Isolating installations with virtual environments to prevent dependency conflicts is recommended.  You can use the Python3 [`venv`](https://docs.python.org/3/library/venv.html) module or [`conda`](https://docs.conda.io/en/latest/miniconda.html), which is shown below.

Create and activate the virtual environment, checking that the chosen Python version is compatible with package requirements

```bash
conda create --name rupture python=3.10
conda activate rupture
```

### From PyPi

The easiest way to install the package is via PyPi. For users interested in a more hands on development environment, instructions for a source installation with optional additional dependencies for development and testing further down.

```bash
pip install esi-utils-rupture
```

### From Source

First clone the repostory locally

```bash
git clone https://code.usgs.gov/ghsc/esi/esi-utils-rupture.git
cd esi-utils-rupture
```

Next, install the code with pip

```bash
pip install .
```

Note that this will install the minimum requirements to run the code.
There are additional optional packages that can be installed that support running the unit tests (`test`), code development (`dev`), and building wheels (`build`).
To install these, you need to add the relevant option in brackets:

```bash
pip install .[test,dev,build]
```

For developers, it is also convenient to install the code in "editable" mode by adding the `-e` option:

```bash
pip install -e .[test,dev,build]
```

## Tests

If you are installing from soruce and included the optional `test` dependencies in the install step, then you can run the unit tests in the root directory of the repository:

```bash
pytest .
```
