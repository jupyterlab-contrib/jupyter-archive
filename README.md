# jupyter-archive

[![Extension status](https://img.shields.io/badge/status-ready-success 'ready to be used')](https://jupyterlab-contrib.github.io/)
[![Github Actions Status](https://github.com/jupyterlab-contrib/jupyter-archive/workflows/Build/badge.svg)](https://github.com/jupyterlab-contrib/jupyter-archive/actions?query=workflow%3ABuild)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jupyterlab-contrib/jupyter-archive.git/master?urlpath=lab)
[![Version](https://img.shields.io/npm/v/@hadim/jupyter-archive.svg)](https://www.npmjs.com/package/@hadim/jupyter-archive)
[![PyPI](https://img.shields.io/pypi/v/jupyter-archive)](https://pypi.org/project/jupyter-archive/)
[![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/jupyter-archive)](https://anaconda.org/conda-forge/jupyter-archive)

A Jupyter extension to make, download and extract archive files.

Features:

- Download selected or current folder as an archive.
- Supported formats: 'zip', 'tar.gz', 'tar.bz2' and 'tar.xz'.
- Archiving and downloading are non-blocking for Jupyter. UI can still be used.
- Archive format can be set in the JLab settings.
- Alternatively, you can choose the format in the file browser menu (the format setting needs to be set to `null`).
- Decompress an archive directly in file browser.
- Notebok client extension not available. [Contributions are welcome](https://github.com/jupyterlab-contrib/jupyter-archive/issues/21).

![jupyter-archive in action](https://raw.githubusercontent.com/jupyterlab-contrib/jupyter-archive/master/archive.gif)

## Configuration

The server extension has some [configuration settings](https://jupyter-server.readthedocs.io/en/latest/users/configuration.html) --
the values below are the default one:

```json5
{
  JupyterArchive: {
    stream_max_buffer_size: 104857600, // The max size of tornado IOStream buffer
    handler_max_buffer_length: 10240, // The max length of chunks in tornado RequestHandler
    archive_download_flush_delay: 100 // The delay in ms at which we send the chunk of data to the client.
  }
}
```

You can also set new values with the following environment variables:

- `JA_IOSTREAM_MAX_BUFFER_SIZE`
- `JA_HANDLER_MAX_BUFFER_LENGTH`
- `JA_ARCHIVE_DOWNLOAD_FLUSH_DELAY`

## Requirements

- JupyterLab >= 3.0 or Notebook >= 7.0

For JupyterLab 2.x, have look [there](https://github.com/jupyterlab-contrib/jupyter-archive/tree/2.x).

## Install

To install the extension, execute:

```bash
pip install jupyter-archive
```

Or

```bash
conda install -c conda-forge jupyter-archive
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall jupyter-archive
```

Or

```bash
conda remove jupyter-archive
```

## Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter server extension list
```

If the server extension is installed and enabled, but you are not seeing
the frontend extension, check the frontend extension is installed:

```bash
jupyter labextension list
```

## Contributing

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the jupyter-archive directory
# Install package in development mode
pip install -e ".[test]"
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Server extension must be manually installed in develop mode
jupyter server extension enable jupyter_archive
# Rebuild extension Typescript source after making changes
jlpm build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

## License

Under BSD license. See [LICENSE](LICENSE).

## Authors

- Hadrien Mary: [@hadim](https://github.com/hadim)
- Frédéric Collonval: [@fcollonval](https://github.com/fcollonval)

### Development uninstall

```bash
# Server extension must be manually disabled in develop mode
jupyter server extension disable jupyter_archive
pip uninstall jupyter-archive
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `@hadim/jupyter-archive` within that folder.

### Testing the extension

#### Server tests

This extension is using [Pytest](https://docs.pytest.org/) for Python code testing.

Install test dependencies (needed only once):

```sh
pip install -e ".[test]"
# Each time you install the Python package, you need to restore the front-end extension link
jupyter labextension develop . --overwrite
```

To execute them, run:

```sh
pytest -vv -r ap --cov jupyter_archive
```

#### Integration tests

This extension uses [Playwright](https://playwright.dev/docs/intro) for the integration tests (aka user level tests).
More precisely, the JupyterLab helper [Galata](https://github.com/jupyterlab/jupyterlab/tree/master/galata) is used to handle testing the extension in JupyterLab.

More information are provided within the [ui-tests](./ui-tests/README.md) README.

### Packaging the extension

See [RELEASE](RELEASE.md)
