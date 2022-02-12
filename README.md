# jupyter-archive

[![Extension status](https://img.shields.io/badge/status-ready-success "ready to be used")](https://jupyterlab-contrib.github.io/)
[![Github Actions Status](https://github.com/jupyterlab-contrib/jupyter-archive/workflows/Build/badge.svg)](https://github.com/jupyterlab-contrib/jupyter-archive/actions?query=workflow%3ABuild)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jupyterlab-contrib/jupyter-archive.git/master?urlpath=lab)
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

## Configuration

The server extension has some [configuration settings](https://jupyter-server.readthedocs.io/en/latest/users/configuration.html) -- 
 the values below are the default one:

```json5
{
  "JupyterArchive": {
    "stream_max_buffer_size": 104857600, // The max size of tornado IOStream buffer
    "handler_max_buffer_length": 10240, // The max length of chunks in tornado RequestHandler
    "archive_download_flush_delay": 100 // The delay in ms at which we send the chunk of data to the client.
  }
}
```

You can also set new values with the following environment variables:

- `JA_IOSTREAM_MAX_BUFFER_SIZE`
- `JA_HANDLER_MAX_BUFFER_LENGTH`
- `JA_ARCHIVE_DOWNLOAD_FLUSH_DELAY`

## Requirements

- JupyterLab >= 3.0

For JupyterLab 2.x, have look [there](https://github.com/jupyterlab-contrib/jupyter-archive/tree/2.x).

## Install

```bash
pip install jupyter-archive
```

Or

```bash
conda install -c conda-forge jupyter-archive
```

## Uninstall

```bash
pip uninstall jupyter-archive
```

Or

```bash
conda remove jupyter-archive
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
pip install -e .
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Server extension must be manually installed in develop mode
jupyter server extension enable jupyter_archive
# Rebuild extension Typescript source after making changes
jlpm run build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm run watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm run build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

## License

Under BSD license. See [LICENSE](LICENSE).

## Authors

- Hadrien Mary: [@hadim](https://github.com/hadim)
- Frédéric Collonval: [@fcollonval](https://github.com/fcollonval)
