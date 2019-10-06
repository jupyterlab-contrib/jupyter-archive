from notebook.utils import url_path_join
from .handlers import DownloadArchiveHandler
from .handlers import ExtractArchiveHandler


# Jupyter Extension points
def _jupyter_server_extension_paths():
  return [{'module': 'jupyter_archive'}]


def load_jupyter_server_extension(nbapp):

  # Add download handler.
  base_url = url_path_join(nbapp.web_app.settings['base_url'], r'/directories/(.*)')
  handlers = [(base_url, DownloadArchiveHandler)]
  nbapp.web_app.add_handlers('.*', handlers)

  # Add extract handler.
  base_url = url_path_join(nbapp.web_app.settings['base_url'], r'/extract-archive/(.*)')
  handlers = [(base_url, ExtractArchiveHandler)]
  nbapp.web_app.add_handlers('.*', handlers)

  nbapp.log.info("jupyter_archive is enabled.")
