# jupyter-archive

[![Build Status](https://travis-ci.com/hadim/jupyter-archive.svg?branch=master)](https://travis-ci.com/hadim/jupyter-archive)
[![Version](https://img.shields.io/npm/v/@hadim/jupyter-archive.svg)](https://www.npmjs.com/package/@hadim/jupyter-archive)
[![PyPI](https://img.shields.io/pypi/v/jupyter-archive)](https://pypi.org/project/jupyter-archive/)

Make, download and extract archive files.

The extension is composed of two extensions:

- A Jupyterlab extension (frontend).
- A Jupyter server extension (backend).

Note that the extension is inspired from [nbzip](https://github.com/data-8/nbzip).

## Prerequisites

- JupyterLab

## Installation

This extension is meant to be integrated into Jupyter. In the meantime you can install it with:

```bash
pip install jupyter-archive
jupyter lab build
```

This will install both the server extension and the labextension needed by this plugin.

You can also install the labextension via Jupyterlab's extension manager GUI. Keep in mind that if you use the GUI, you'll still need to install the `jupyterlab-archive` server extension via `pip`.

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

## License

Under BSD license. See [LICENSE](LICENSE).

## Release a new version

- Edit `jupyter_archive/_version.py` and set the version.
- Edit `package.json` and set the version.
- Commit `git commit -am "Bump to <your_version>"`
- Tag: `git tag <your_version>`
- Upload to NPM: `yarn publish --access=public`
- Build Python package: `rm -fr dist/ && python setup.py sdist bdist_wheel`
- Upload Python package: `twine upload dist/*`

- Edit `jupyter_archive/_version.py` and set the version back to `.dev0`.
- Edit `package.json` and set the version back to `-dev`.
- Commit `git commit -am "Bump to dev"`
- Push: `git push origin master --tags`
