# benchviper
Performance monitoring for xradio

This repository uses airspeed-velocity to benchmark packages in the VIPER ecosystem.

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

After populating `asv.conf.json` with the values that reference the correct project, it can be run using `asv run --verbose`.

Note: for `xradio`, the environment building commands disqualify running benchmarks using [asv's environment isolation](https://asv.readthedocs.io/en/latest/using.html#environments] on macOS (unless "environment_type" is set to "existing"). This is due to the dependencies requiring pre-installation of `python-casacore` from conda-forge before running the regular wheel building commands (which still to be [specified](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/#build-time-dependencies) in [xradio/pyproject.toml](https://github.com/casangi/xradio/blob/main/pyproject.toml). 
