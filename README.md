# jupyter-archive

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jupyterlab-contrib/jupyter-archive/master?urlpath=lab)
[![Build Status](https://travis-ci.com/hadim/jupyter-archive.svg?branch=master)](https://travis-ci.com/hadim/jupyter-archive)
[![Version](https://img.shields.io/npm/v/@hadim/jupyter-archive.svg)](https://www.npmjs.com/package/@hadim/jupyter-archive)
[![PyPI](https://img.shields.io/pypi/v/jupyter-archive)](https://pypi.org/project/jupyter-archive/)
[![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/jupyter-archive)](https://anaconda.org/conda-forge/jupyter-archive)

A Jupyterlab extension to make, download and extract archive files.

Features:

- Download selected or current folder as an archive.
- Supported formats: 'zip', 'tar.gz', 'tar.bz2' and 'tar.xz'.
- Archiving and downloading are non-blocking for Jupyter. UI can still be used.
- Archive format can be set in the JLab settings.
- Alternatively, you can choose the format in the file browser menu (the format setting needs to be set to `null`).
- Decompress an archive directly in file browser.
- Notebok client extension not available. [Contributions are welcome](https://github.com/jupyterlab-contrib/jupyter-archive/issues/21).

![jupyter-archive in action](https://raw.githubusercontent.com/jupyterlab-contrib/jupyter-archive/master/archive.gif)

## Prerequisites

- JupyterLab >=2.0.0,<3.0.0

## Installation

Using `pip`:

```bash
pip install jupyter-archive
jupyter lab build
```

Using `conda`:

```bash
conda install -c conda-forge nodejs jupyter-archive
jupyter lab build
```

This will install both the server extension and the Jupyterlab extension needed by the plugin.

You can also install the labextension via Jupyterlab's extension manager GUI. Keep in mind that if you use the GUI, you'll still need to install the `jupyter-archive` server extension via `pip` or `conda`.

## Development

Install dependencies with conda:

```bash
conda env update -f environment.yml
```

For a development install (requires npm version 4 or later), do the following in the repository directory:

```bash
jlpm
jlpm build
jupyter labextension link .

# Install the server extension
pip install -e .
jupyter serverextension enable --py jupyter_archive
```

You can watch the source directory and run JupyterLab in watch mode to watch for changes in the extension's source and automatically rebuild the extension and application.

```bash
# Watch the source directory in another terminal tab
jlpm watch

# Run jupyterlab in watch mode in one terminal tab
jupyter lab --watch --no-browser --NotebookApp.token=''
```

Test the server extension:

```bash
pytest -v jupyter_archive/tests/
```

## License

Under BSD license. See [LICENSE](LICENSE).

## Authors

- Hadrien Mary: [@hadim](https://github.com/hadim)
- Frédéric Collonval: [@fcollonval](https://github.com/fcollonval)

## Release a new version

- Install [rever](https://regro.github.io/rever-docs/index.html) and twine: `conda install rever twine`
- Run: `rever <VERSION>`
