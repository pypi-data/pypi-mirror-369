# defopt-stubs

Typing stubs for the [defopt](https://github.com/anntzer/defopt) package.

These stubs provide type hints for the runtime library, which does not
ship with annotations. Only the minimal API used by typical scripts is
covered. Contributions to improve coverage are welcome.

## Installation

```
pip install defopt-stubs
```

## Development

Stubs are located under `stubs/defopt-stubs`. After installing development
dependencies with `uv`, validate them by running `mypy`:

```
uv sync
mypy
python tests/test_script.py 42 --times 1
```

`uv sync` installs the runtime library and tooling required for type
checking. The CI workflow performs the same steps.

## Publishing

Releases are automated via GitHub Actions. Create a git tag starting
with `v` (e.g. `v0.1.0`) and push it to trigger a PyPI upload. A
`PYPI_TOKEN` secret must be configured in the repository settings.
