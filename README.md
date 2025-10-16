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
# configured to use "standalone repo" option, which creates asv.conf.json
```
> [!NOTE]
> For `xradio`, the environment building commands disqualify running benchmarks using [asv's environment isolation](https://asv.readthedocs.io/en/latest/using.html#environments) on macOS (unless "environment_type" is set to "existing"). This is due to the dependencies requiring pre-installation of `python-casacore` from conda-forge before running the regular wheel building commands (which still to be [specified](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/#build-time-dependencies) in [xradio/pyproject.toml](https://github.com/casangi/xradio/blob/main/pyproject.toml)).

## Running and publishing benchmarks
After populating `asv.conf.json` with values that reference the correct project, benchmarks may be run using `asv run --verbose`.

Association of results with a particular entry in the results database is possible using the [`asv machine`](https://asv.readthedocs.io/en/stable/using.html#machine-information) command and by passing a value to the `--machine` argument of `asv run` (e.g., uniform configuration of github-actions test VMs to register as the "same" platform).

After test results have been collected, the JSON results can be processed into static HTML using `asv publish`. This can be hosted locally using `asv preview`. Tracking of results on a dedicated `gh-pages` branch (using the [`asv gh-pages`](https://asv.readthedocs.io/en/stable/commands.html#asv-gh-pages) command) will [require a Github Enterprise license](https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site) unless the repository has Public visibility.

Dedication of an on-premises test machine connected to this repository as a self-hosted runner has been verified, but disabled pending migration to organization level deployment of [actions-runner-controller](https://docs.github.com/en/actions/concepts/runners/actions-runner-controller) runner pool.

## Interaction with parent repositories

> [!NOTE]
> Hooks to trigger automated testing for integration with PR workflows and reporting on CI dashboards can be configured using an additional dispatch mechanism in [testviper/.github/workflows/dispatch-receiver.yml](https://github.com/casangi/testviper/blob/main/.github/workflows/dispatch-receiver.yml). This is under development.
