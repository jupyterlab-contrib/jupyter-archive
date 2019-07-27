# jupyter-archive

[![Build Status](https://travis-ci.com/hadim/jupyter-archive.svg?branch=master)](https://travis-ci.com/hadim/jupyter-archive)

Download folder as archive file.

The extension is composed of two extensions:

- A Jupyterlab extension (frontend).
- A Jupyter server extension (backend).

Note that the extension is largely inspired from [nbzip](https://github.com/data-8/nbzip).

## Prerequisites

- JupyterLab

## Installation

This extension is meant to be integrated into Jupyter so there is no JLab or PyPi releases. Check the dev section for installation.

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
pytest jupyter_archive/tests/
```
