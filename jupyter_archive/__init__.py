import os

from notebook.utils import url_path_join
from traitlets.config import Configurable
from traitlets import Int, default

from .handlers import DownloadArchiveHandler
from .handlers import ExtractArchiveHandler


# Jupyter Extension points
def _jupyter_server_extension_paths():
    return [{"module": "jupyter_archive"}]


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


def load_jupyter_server_extension(nbapp):
    config = JupyterArchive(config=nbapp.config)
    nbapp.web_app.settings["jupyter_archive"] = config

    # Add download handler.
    base_url = url_path_join(nbapp.web_app.settings["base_url"], r"/directories/(.*)")
    handlers = [(base_url, DownloadArchiveHandler)]
    nbapp.web_app.add_handlers(".*", handlers)

    # Add extract handler.
    base_url = url_path_join(nbapp.web_app.settings["base_url"], r"/extract-archive/(.*)")
    handlers = [(base_url, ExtractArchiveHandler)]
    nbapp.web_app.add_handlers(".*", handlers)

    nbapp.log.info("jupyter_archive is enabled.")
