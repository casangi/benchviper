## github actions
This area contains the workflow definition files that run in github actions.

### xradio.yaml
This file defines the workflow that runs daily to check for merge commits in xradio and runs _new_ combinations of 
- environment (defined by asv.conf.json)
- commit (defined by the range specified in the `asv run command`
- test (defined by the contents of xradio/benchmarks of this repository, on the main branch)

### xradio-branch.yaml
This file defines the workflow that is triggered on demand to run only _the latest_ commit on a given development branch.

See the documentation on the [`--skip-existing`](https://asv.readthedocs.io/en/stable/commands.html#asv-run) parameter for more details on how the `asv run` invocations interact with the results database.