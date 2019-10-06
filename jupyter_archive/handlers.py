import os
import asyncio
import zipfile
import tarfile
import pathlib

from tornado import gen, web, iostream
from notebook.base.handlers import IPythonHandler
from notebook.utils import url2path


class ArchiveStream:
    def __init__(self, handler):
        self.handler = handler
        self.position = 0

    def write(self, data):
        self.position += len(data)
        self.handler.write(data)

    def tell(self):
        return self.position

    def flush(self):
        self.handler.flush()


def make_writer(handler, archive_format="zip"):
    fileobj = ArchiveStream(handler)

    if archive_format == "zip":
        archive_file = zipfile.ZipFile(fileobj, mode="w")
        archive_file.add = archive_file.write
    elif archive_format == "tar.gz":
        archive_file = tarfile.open(fileobj=fileobj, mode="w:gz")
    elif archive_format == "tar.bz2":
        archive_file = tarfile.open(fileobj=fileobj, mode="w:bz2")
    elif archive_format == "tar.xz":
        archive_file = tarfile.open(fileobj=fileobj, mode="w:xz")
    else:
        raise ValueError("'{}' is not a valid archive format.".format(archive_format))
    return archive_file


class ArchiveHandler(IPythonHandler):

    @web.authenticated
    async def get(self, archive_path):

        # /directories/ requests must originate from the same site
        self.check_xsrf_cookie()
        cm = self.contents_manager

        if cm.is_hidden(archive_path) and not cm.allow_hidden:
            self.log.info("Refusing to serve hidden file, via 404 Error")
            raise web.HTTPError(404)

        archive_token = self.get_argument("archiveToken")
        archive_format = self.get_argument("archiveFormat", "zip")

        fullpath = os.path.join(cm.root_dir, url2path(archive_path))

        archive_path = pathlib.Path(archive_path)
        archive_name = archive_path.name
        archive_filename = archive_path.with_suffix(".{}".format(archive_format)).name

        # We gonna send out event streams!
        self.set_header("content-type", "application/octet-stream")
        self.set_header("cache-control", "no-cache")
        self.set_header(
            "content-disposition", "attachment; filename={}".format(archive_filename)
        )

        self.log.debug(
            "Prepare {} for archiving and downloading.".format(archive_filename)
        )

        with make_writer(self, archive_format) as zipf:
            prefix = len(str(pathlib.Path(fullpath).parent))
            for root, dirs, files in os.walk(fullpath):
                for file_ in files:
                    file_name = os.path.join(root, file_)
                    self.log.debug("{}\n".format(file_name))
                    zipf.add(file_name, os.path.join(root[prefix + len(os.path.sep):], file_))

        self.set_cookie("archiveToken", archive_token)
        self.log.debug("Finished downloading {}.".format(archive_filename))
        self.finish()
