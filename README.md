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


## Running and publishing benchmarks

After populating `asv.conf.json` with values that reference the correct project, benchmarks may be invoked using the `asv` executable. To run all the benchmarks, use something like [`asv run --verbose`](https://asv.readthedocs.io/en/stable/commands.html#asv-run). This assumes you have already configured your machine, but if not then you will be prompted to do so. If results for your machine are not already tracked in source control (i.e., a directory in benchviper/xradio/results/) then all benchmarks will run for the history of the project. To specify only a certain subset of commits to test, use the range argument (as in the workflow files used by the CI system).

Association of results with a particular entry in the results database is possible using the [`asv machine`](https://asv.readthedocs.io/en/stable/using.html#machine-information) command and by passing a value to the `--machine` argument of `asv run` (e.g., uniform configuration of github-actions test VMs to register as the "same" platform). This can be helpful in cases where you want to locally publish and preview the results for the gh-runner machine -- for example, if you want to test the command used by the CI system, but run it for all historical commits after v0.0.49 rather than just since v1.0.2, you can do that like this:
```
asv machine --machine gh-runner --yes
asv run "--merges v0.0.49..main" --machine gh-runner --parallel --interleave-rounds
# Note that the `--skip-existing` keyword has been omitted, so force the asv runner to re-run tests.
```

After test results have been collected, the JSON results can be processed into static HTML using `asv publish`. This can be hosted locally using `asv preview`. Tracking of results on a dedicated `gh-pages` branch is implemented for this repository and deployed to [here](https://casangi.github.io/benchviper/).

Dedication of an on-premises test machine connected to this repository as a self-hosted runner has been verified, but disabled pending migration to organization level deployment of [actions-runner-controller](https://docs.github.com/en/actions/concepts/runners/actions-runner-controller) runner pool.

> [!WARNING]
> When changing a benchmark, if there is no version attribute already assigned to a given tests, than _any_ change to the test code will cause asv to register it as a new version of the test. This is because all code (including setup, whitespace, and comments) is hashed and stored in the version parameter of xradio/results/benchmarks.json. Special care should be taken to ensure backward compatibility.
> 
> See these pages in the [asv docs](https://asv.readthedocs.io/en/stable/writing_benchmarks.html) and [numpy repository](https://github.com/numpy/numpy/tree/main/benchmarks#writing-benchmarks) for more details on best practices for writing good benchmarks.

## Interaction with parent repositories

> [!NOTE]
> The GitHub Actions on this repository are triggered via a dispatch mechanism that is received in [.github/workflows/dispatch-receiver.yaml](https://github.com/casangi/benchviper/blob/main/.github/workflows/dispatch-receiver.yaml). 
