## github actions
This area contains the workflow definition files that run in github actions.

### xradio.yaml
This file defines the workflow that runs daily to check for merge commits in xradio and runs _new_ combinations of 
- environment (defined by asv.conf.json)
- commit (defined by the range specified in the `asv run command`
- test (defined by the contents of xradio/benchmarks of this repository, on the main branch)

The workflow also deploys benchmark results to GitHub Pages at `https://[org].github.io/benchviper/xradio/` using the `peaceiris/actions-gh-pages@v4` action. The deployment:
- Publishes HTML from `xradio/html/` to the `xradio` subfolder on the `gh-pages` branch
- Only deploys when running on the `main` branch
- Uses `keep_files: true` to preserve benchmark results from other projects

### xradio-branch.yaml
This file defines the workflow that is triggered on demand to run only _the latest_ commit on a given development branch.

### Future Projects
When adding benchmarks for additional projects (e.g., astroviper), create a new workflow file following the same pattern:
- Set `publish_dir: ./astroviper/html`
- Set `destination_dir: astroviper`
- Keep `keep_files: true` to allow multiple projects to coexist on gh-pages
- Each project will be accessible at `https://[org].github.io/benchviper/[project-name]/`

See the documentation on the [`--skip-existing`](https://asv.readthedocs.io/en/stable/commands.html#asv-run) parameter for more details on how the `asv run` invocations interact with the results database.