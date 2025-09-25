# benchviper
Performance monitoring for xradio

This repository uses airspeed-velocity ([asv](https://asv.readthedocs.io/en/stable/)) to benchmark packages in the [VIPER](https://github.com/casangi) ecosystem.

## Configuring asv for a project

```
mkdir -p benchviper && cd $_
micromamba env create --name benchviper
micromamba activate benchviper
micromamba install python==3.12
micromamba install asv

asv quickstart
# configured to use "option 1" (standalone repo), which creates asv.conf.json
```
> [!NOTE]
> For `xradio`, the environment building commands disqualify running benchmarks using [asv's environment isolation](https://asv.readthedocs.io/en/latest/using.html#environments) on macOS (unless "environment_type" is set to "existing"). This is due to the dependencies requiring pre-installation of `python-casacore` from conda-forge before running the regular wheel building commands (which still to be [specified](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/#build-time-dependencies) in [xradio/pyproject.toml](https://github.com/casangi/xradio/blob/main/pyproject.toml)).

## Running and publishing benchmarks
After populating `asv.conf.json` with values that reference the correct project, benchmarks may be run using `asv run --verbose`.

> [!NOTE]
> Uniform configuration of github-actions test VMs to register as the "same" platform (i.e., a single entry in the asv results database) using `asv machine` is still under development.

> [!NOTE]
> Dedication of an on-premises test machine connected to this repository using the [actions-runner-controller](https://docs.github.com/en/actions/concepts/runners/actions-runner-controller) mechanism is under preliminary investigation.

After manual or automated results have been measures, they can be processed into static HTML using `asv publish`. This can be hosted locally using `asv preview`. 

> [!NOTE]
> Dedicated `gh-pages` branch to be configured with collected results for each project for compatibility with future extension for testing other repository subdirectories.

## Interaction with parent repositories

> [!NOTE]
> Hooks to trigger automated testing for integration with PR workflows and reporting on CI dashboards can be configured using an additional dispatch mechanism in [testviper/.github/workflows/dispatch-receiver.yml](https://github.com/casangi/testviper/blob/main/.github/workflows/dispatch-receiver.yml)
