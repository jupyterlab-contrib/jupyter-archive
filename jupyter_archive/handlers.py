import os
import asyncio
import time
import zipfile
import tarfile
import pathlib
from urllib.parse import quote

from tornado import gen, web, iostream, ioloop
from notebook.base.handlers import IPythonHandler
from notebook.utils import url2path

# The delay in ms at which we send the chunk of data
# to the client.
ARCHIVE_DOWNLOAD_FLUSH_DELAY = 100
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


class DownloadArchiveHandler(IPythonHandler):
    @property
    def stream_max_buffer_size(self):
        return self.settings["jupyter_archive"].stream_max_buffer_size

    @property
    def handler_max_buffer_length(self):
        return self.settings["jupyter_archive"].handler_max_buffer_length

    @property
    def archive_download_flush_delay(self):
        return self.settings["jupyter_archive"].archive_download_flush_delay

    def flush(self, include_footers=False):
        # skip flush when stream_buffer is larger than stream_max_buffer_size
        stream_buffer = self.request.connection.stream._write_buffer
        if stream_buffer and len(stream_buffer) > self.stream_max_buffer_size:
            return
        return super(DownloadArchiveHandler, self).flush(include_footers)

    @web.authenticated
    @gen.coroutine
    def get(self, archive_path, include_body=False):

        # /directories/ requests must originate from the same site
        self.check_xsrf_cookie()
        cm = self.contents_manager

        if cm.is_hidden(archive_path) and not cm.allow_hidden:
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
        self.flush_cb = ioloop.PeriodicCallback(self.flush, ARCHIVE_DOWNLOAD_FLUSH_DELAY)
        self.flush_cb.start()

        args = (archive_path, archive_format, archive_token, follow_symlinks, download_hidden)
        yield ioloop.IOLoop.current().run_in_executor(None, self.archive_and_download, *args)

        if self.canceled:
            self.log.info("Download canceled.")
        else:
            self.flush()
            self.log.info("Finished downloading {}.".format(archive_filename))

        self.set_cookie("archiveToken", archive_token)
        self.flush_cb.stop()
        self.finish()

    def archive_and_download(self, archive_path, archive_format, archive_token, follow_symlinks, download_hidden):

        with make_writer(self, archive_format) as archive:
            prefix = len(str(archive_path.parent)) + len(os.path.sep)
            for root, dirs, files in os.walk(archive_path, followlinks=follow_symlinks):
                # This ensures that if download_hidden is false, then the
                # hidden files are skipped when walking the directory.
                if not download_hidden:
                    files = [f for f in files if not f[0] == '.']
                    dirs[:] = [d for d in dirs if not d[0] == '.']
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


class ExtractArchiveHandler(IPythonHandler):
    @web.authenticated
    @gen.coroutine
    def get(self, archive_path, include_body=False):
        # /extract-archive/ requests must originate from the same site
        self.check_xsrf_cookie()
        cm = self.contents_manager

        if cm.is_hidden(archive_path) and not cm.allow_hidden:
            self.log.info("Refusing to serve hidden file, via 404 Error")
            raise web.HTTPError(404)

        archive_path = pathlib.Path(cm.root_dir) / url2path(archive_path)

        yield ioloop.IOLoop.current().run_in_executor(None, self.extract_archive, archive_path)

        self.finish()

    def extract_archive(self, archive_path):
        archive_destination = archive_path.parent
        self.log.info("Begin extraction of {} to {}.".format(archive_path, archive_destination))

        archive_reader = make_reader(archive_path)
        with archive_reader as archive:
            archive.extractall(archive_destination)

        self.log.info("Finished extracting {} to {}.".format(archive_path, archive_destination))
