# Installation

## Simple Install
### uv/pip (recommended)

```console
$ uv add torch-named-linops
# or
$ pip install torch-named-linops
```

:::{note}
Cupy doesn't like `nccl` dependencies installed as wheels from pip. Importing
cupy the first time will present an import error with a python command that can
be used to manually install the nccl library, e.g. (for cuda 12.x - replace with
relevant cuda version)

```console
$ python -m cupyx.tools.install_library --library nccl --cuda 12.x
```

For more up-to-date info, can follow the issue [here](https://github.com/cupy/cupy/issues/8227).
:::
## Installing from source (development)
Clone the repo, then choose from the following:

### uv
```console
$ uv add --editable path/to/torch-named-linops

# or

$ pip install -e path/to/torch-named-linops
```
This will install the library in
[editable mode.](https://docs.astral.sh/uv/concepts/projects/dependencies/#editable-dependencies)

### Notes for development
- Installation with optional dependency specifiers:
  - `[dev]` - installs with development capabilities (e.g. docs, pytest, cov)
  - `[sigpy]` - installs with sigpy to enable unit testing against `sp.ArrayToBlocks` and `sp.Interpolate`
    - Careful doing this, as [sigpy](https://github.com/mikgroup/sigpy) might not like certain package versions of things.
  - `[all]` - installs all optional dependencies!
