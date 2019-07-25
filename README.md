# jupyter-archive

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

For a development install (requires npm version 4 or later), do the following in the repository directory:

```bash
npm install
npm run build
jupyter labextension link .

# Install the server extension
pip install -e .
jupyter serverextension enable --py jupyter_archive
```

To rebuild the package and the JupyterLab app:

```bash
npm run build
jupyter lab build
```
