import os

from traitlets.config import Configurable
from traitlets import Int, default

try:
    from ._version import __version__
except ImportError:
    # Fallback when using the package in dev mode without installing
    # in editable mode with pip. It is highly recommended to install
    # the package from a stable release or in editable mode: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
    import warnings
    warnings.warn("Importing 'jupyter-archive' outside a proper installation.")
    __version__ = "dev"
from .handlers import setup_handlers


def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "@hadim/jupyter-archive"
    }]


def _jupyter_server_extension_points():
    return [{
        "module": "jupyter_archive"
    }]


class JupyterArchive(Configurable):
    stream_max_buffer_size = Int(help="The max size of tornado IOStream buffer",
                                 config=True)

    @default("stream_max_buffer_size")
    def _default_stream_max_buffer_size(self):
        # 100 * 1024 * 1024 equals to 100M
        return int(os.environ.get("JA_IOSTREAM_MAX_BUFFER_SIZE", 100 * 1024 * 1024))

    handler_max_buffer_length = Int(help="The max length of chunks in tornado RequestHandler",
                                    config=True)

    @default("handler_max_buffer_length")
    def _default_handler_max_buffer_length(self):
        # if 8K for one chunk, 10240 * 8K equals to 80M
        return int(os.environ.get("JA_HANDLER_MAX_BUFFER_LENGTH", 10240))

    archive_download_flush_delay = Int(help="The delay in ms at which we send the chunk of data to the client.",
                                       config=True)

    @default("archive_download_flush_delay")
    def _default_archive_download_flush_delay(self):
        return int(os.environ.get("JA_ARCHIVE_DOWNLOAD_FLUSH_DELAY", 100))


def _load_jupyter_server_extension(server_app):
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    config = JupyterArchive(config=server_app.config)
    server_app.web_app.settings["jupyter_archive"] = config
    setup_handlers(server_app.web_app)
