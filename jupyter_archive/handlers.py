import json
import os
import pathlib
import tarfile
import time
import traceback
import zipfile
import threading
from http.client import responses

from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url2path, url_path_join, ensure_async
from tornado import ioloop, web
from urllib.parse import quote

SUPPORTED_FORMAT = [
    "zip",
    "tgz",
    "tar.gz",
    "tbz",
    "tbz2",
    "tar.bz",
    "tar.bz2",
    "txz",
    "tar.xz",
]


class ArchiveStream:
    def __init__(self, handler):
        self.handler = handler
        self.position = 0

    def write(self, data):
        if self.handler.canceled:
            raise ValueError("File download canceled")
        # timeout 600s for this while loop
        time_out_cnt = 600 * 1000 / self.handler.archive_download_flush_delay
        while len(self.handler._write_buffer) > self.handler.handler_max_buffer_length:
            # write_buffer or handler is too large, wait for an flush cycle
            time.sleep(self.handler.archive_download_flush_delay / 1000)
            if self.handler.canceled:
                raise ValueError("File download canceled")
            time_out_cnt -= 1
            if time_out_cnt <= 0:
                raise ValueError("Time out for writing into tornado buffer")
        self.position += len(data)
        with self.handler.lock:
            self.handler.write(data)
        del data

    def tell(self):
        return self.position

    def flush(self):
        # Note: Flushing is done elsewhere, in the main thread
        # because `write()` is called in a background thread.
        # self.handler.flush()
        pass


def make_writer(handler, archive_format="zip"):
    fileobj = ArchiveStream(handler)

    if archive_format == "zip":
        archive_file = zipfile.ZipFile(fileobj, mode="w", compression=zipfile.ZIP_DEFLATED)
        archive_file.add = archive_file.write
    elif archive_format in ["tgz", "tar.gz"]:
        archive_file = tarfile.open(fileobj=fileobj, mode="w|gz")
    elif archive_format in ["tbz", "tbz2", "tar.bz", "tar.bz2"]:
        archive_file = tarfile.open(fileobj=fileobj, mode="w|bz2")
    elif archive_format in ["txz", "tar.xz"]:
        archive_file = tarfile.open(fileobj=fileobj, mode="w|xz")
    else:
        raise ValueError("'{}' is not a valid archive format.".format(archive_format))
    return archive_file


def make_reader(archive_path):

    archive_format = "".join(archive_path.suffixes)

    if archive_format.endswith(".zip"):
        archive_file = zipfile.ZipFile(archive_path, mode="r")
    elif any([archive_format.endswith(ext) for ext in [".tgz", ".tar.gz"]]):
        archive_file = tarfile.open(archive_path, mode="r|gz")
    elif any([archive_format.endswith(ext) for ext in [".tbz", ".tbz2", ".tar.bz", ".tar.bz2"]]):
        archive_file = tarfile.open(archive_path, mode="r|bz2")
    elif any([archive_format.endswith(ext) for ext in [".txz", ".tar.xz"]]):
        archive_file = tarfile.open(archive_path, mode="r|xz")
    else:
        raise ValueError("'{}' is not a valid archive format.".format(archive_format))
    return archive_file


class DownloadArchiveHandler(JupyterHandler):
    lock = threading.Lock()

    @property
    def stream_max_buffer_size(self):
        return self.settings["jupyter_archive"].stream_max_buffer_size

    @property
    def handler_max_buffer_length(self):
        return self.settings["jupyter_archive"].handler_max_buffer_length

    @property
    def archive_download_flush_delay(self):
        return self.settings["jupyter_archive"].archive_download_flush_delay

    def flush(self, include_footers=False, force=False):
        # skip flush when stream_buffer is larger than stream_max_buffer_size
        stream_buffer = self.request.connection.stream._write_buffer
        if not force and stream_buffer and len(stream_buffer) > self.stream_max_buffer_size:
            return
        with self.lock:
            return super(DownloadArchiveHandler, self).flush(include_footers)

    @web.authenticated
    async def get(self, archive_path, include_body=False):

        # /directories/ requests must originate from the same site
        self.check_xsrf_cookie()
        cm = self.contents_manager

        if await ensure_async(cm.is_hidden(archive_path)) and not cm.allow_hidden:
            self.log.info("Refusing to serve hidden file, via 404 Error")
            raise web.HTTPError(404)

        archive_token = self.get_argument("archiveToken")
        archive_format = self.get_argument("archiveFormat", "zip")
        if archive_format not in SUPPORTED_FORMAT:
            self.log.error("Unsupported format {}.".format(archive_format))
            raise web.HTTPError(404)
        # Because urls can only pass strings, must check if string value is true
        # or false. If it is not either value, then it is an invalid argument
        # and raise http error 400.
        if self.get_argument("followSymlinks", "true") == "true":
            follow_symlinks = True
        elif self.get_argument("followSymlinks", "true") == "false":
            follow_symlinks = False
        else:
            raise web.HTTPError(400)
        if self.get_argument("downloadHidden", "false") == "true":
            download_hidden = True
        elif self.get_argument("downloadHidden", "false") == "false":
            download_hidden = False
        else:
            raise web.HTTPError(400)

        archive_path = pathlib.Path(cm.root_dir) / url2path(archive_path)
        archive_filename = f"{archive_path.name}.{archive_format}"
        archive_filename = quote(archive_filename)

        self.log.info("Prepare {} for archiving and downloading.".format(archive_filename))
        self.set_header("content-type", "application/octet-stream")
        self.set_header("cache-control", "no-cache")
        self.set_header("content-disposition", "attachment; filename={}".format(archive_filename))

        self.canceled = False
        self.flush_cb = ioloop.PeriodicCallback(self.flush, self.archive_download_flush_delay)
        self.flush_cb.start()

        try:
            args = (
                archive_path,
                archive_format,
                archive_token,
                follow_symlinks,
                download_hidden,
            )
            await ioloop.IOLoop.current().run_in_executor(None, self.archive_and_download, *args)

            if self.canceled:
                self.log.info("Download canceled.")
            else:
                # Here, we need to flush forcibly to move all data from _write_buffer to stream._write_buffer
                self.flush(force=True)
                self.log.info("Finished downloading {}.".format(archive_filename))
        except Exception:
            raise
        finally:
            self.flush_cb.stop()

        self.set_cookie("archiveToken", archive_token)
        self.finish()

    def archive_and_download(
        self,
        archive_path,
        archive_format,
        archive_token,
        follow_symlinks,
        download_hidden,
    ):

        with make_writer(self, archive_format) as archive:
            prefix = len(str(archive_path.parent)) + len(os.path.sep)
            for root, dirs, files in os.walk(archive_path, followlinks=follow_symlinks):
                # This ensures that if download_hidden is false, then the
                # hidden files are skipped when walking the directory.
                if not download_hidden:
                    files = [f for f in files if not f[0] == "."]
                    dirs[:] = [d for d in dirs if not d[0] == "."]
                for file_ in files:
                    file_name = os.path.join(root, file_)
                    if not self.canceled:
                        self.log.debug("{}\n".format(file_name))
                        archive.add(file_name, os.path.join(root[prefix:], file_))
                    else:
                        break

    def on_connection_close(self):
        super().on_connection_close()
        self.canceled = True
        self.flush_cb.stop()


class ExtractArchiveHandler(JupyterHandler):
    @web.authenticated
    async def get(self, archive_path, include_body=False):

        # /extract-archive/ requests must originate from the same site
        self.check_xsrf_cookie()
        cm = self.contents_manager

        if await ensure_async(cm.is_hidden(archive_path)) and not cm.allow_hidden:
            self.log.info("Refusing to serve hidden file, via 404 Error")
            raise web.HTTPError(404)

        archive_path = pathlib.Path(cm.root_dir) / url2path(archive_path)

        await ioloop.IOLoop.current().run_in_executor(None, self.extract_archive, archive_path)

        self.finish()

    def extract_archive(self, archive_path):

        archive_destination = archive_path.parent
        self.log.info("Begin extraction of {} to {}.".format(archive_path, archive_destination))

        archive_reader = make_reader(archive_path)

        if isinstance(archive_reader, tarfile.TarFile):
            # Check file path to avoid path traversal
            # See https://nvd.nist.gov/vuln/detail/CVE-2007-4559
            with archive_reader as archive:
                for name in archive_reader.getnames():
                    if os.path.relpath(archive_destination / name, archive_destination).startswith(os.pardir):
                        error_message = f"The archive file includes an unsafe file path: {name}"
                        self.log.error(error_message)
                        raise web.HTTPError(400, reason=error_message)
            # Re-open stream
            archive_reader = make_reader(archive_path)

        with archive_reader as archive:
            archive.extractall(archive_destination)

        self.log.info("Finished extracting {} to {}.".format(archive_path, archive_destination))

    def write_error(self, status_code, **kwargs):
        # Return error response as JSON
        # See https://github.com/pyenv/pyenv/blob/ff9d3ca69ef5006352cadc31e57f51aca42705a6/versions/3.8.12/lib/python3.8/site-packages/jupyter_server/base/handlers.py#L610
        self.set_header("Content-Type", "application/json")
        message = responses.get(status_code, "Unknown HTTP Error")
        reply = {
            "message": message,
        }
        exc_info = kwargs.get("exc_info")
        if exc_info:
            e = exc_info[1]
            if isinstance(e, web.HTTPError):
                reply["message"] = e.log_message or message
                reply["reason"] = e.reason
            else:
                reply["message"] = "Unhandled error"
                reply["reason"] = None
                reply["traceback"] = "".join(traceback.format_exception(*exc_info))
        self.finish(json.dumps(reply))


def setup_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    handlers = [
        (url_path_join(base_url, r"/directories/(.*)"), DownloadArchiveHandler),
        (url_path_join(base_url, r"/extract-archive/(.*)"), ExtractArchiveHandler),
    ]
    web_app.add_handlers(host_pattern, handlers)
