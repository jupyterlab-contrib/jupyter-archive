import json
import pathlib
import os

from traitlets.config import Configurable
from traitlets import Int, default

from ._version import __version__
from .handlers import setup_handlers

HERE = pathlib.Path(__file__).parent.resolve()

with (HERE / "labextension" / "package.json").open() as fid:
    data = json.load(fid)


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": data["name"]}]


class JupyterArchive(Configurable):
    stream_max_buffer_size = Int(help="The max size of tornado IOStream buffer")

    @default("stream_max_buffer_size")
    def _default_stream_max_buffer_size(self):
        # 100 * 1024 * 1024 equals to 100M
        return int(os.environ.get("JA_IOSTREAM_MAX_BUFFER_SIZE", 100 * 1024 * 1024))

    handler_max_buffer_length = Int(help="The max length of chunks in tornado RequestHandler")

    @default("handler_max_buffer_length")
    def _default_handler_max_buffer_length(self):
        # if 8K for one chunk, 10240 * 8K equals to 80M
        return int(os.environ.get("JA_HANDLER_MAX_BUFFER_LENGTH", 10240))


def _jupyter_server_extension_points():
    return [{"module": "jupyter_archive"}]


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


# For backward compatibility
load_jupyter_server_extension = _load_jupyter_server_extension
