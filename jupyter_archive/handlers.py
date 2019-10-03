import os
import zipfile
import tarfile
import pathlib

from tornado import gen, web, iostream
from notebook.base.handlers import IPythonHandler


class ArchiveStream():
    def __init__(self, handler):
        self.handler = handler
        self.position = 0

    def write(self, data):
        self.position += len(data)
        self.handler.write(data)

    def tell(self):
        return self.position

    async def flush(self):
        await self.handler.flush()


def make_writer(handler, archive_format="zip"):
    fileobj = ArchiveStream(handler)

    if archive_format == "zip":
        archive_file = zipfile.ZipFile(fileobj, mode='w')
        archive_file.add = archive_file.write
    elif archive_format == "tgz":
        archive_file = tarfile.open(fileobj=fileobj, mode='w|gz')
    elif archive_format == "tbz":
        archive_file = tarfile.open(fileobj=fileobj, mode='w|bz2')
    elif archive_format == "txz":
        archive_file = tarfile.open(fileobj=fileobj, mode='w|xz')
    else:
        raise ValueError("'{}' is not a valid archive format.".format(archive_format))
    return archive_file


class ArchiveHandler(IPythonHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @web.authenticated
    async def get(self):

        # TODO: Switch everything to pathlib.

        archive_path = self.get_argument('archivePath')
        archive_token = self.get_argument('archiveToken')
        archive_format = self.get_argument('archiveFormat', 'zip')

        archive_path = pathlib.Path(archive_path)
        archive_name = archive_path.name
        archive_filename = archive_path.with_suffix(".{}".format(archive_format)).name

        # We gonna send out event streams!
        self.set_header('content-type', 'application/octet-stream')
        self.set_header('cache-control', 'no-cache')
        self.set_header(
            'content-disposition',
            'attachment; filename={}'.format(archive_filename)
        )

        try:
            self.log.info('Prepare {} for archiving and downloading.'.format(archive_filename))
            archive_writer = make_writer(self, archive_format)

            with archive_writer as writer:
                for file_path in archive_path.rglob("*"):
                    writer.add(file_path, file_path.relative_to(archive_path))
                    await self.flush()

        except iostream.StreamClosedError:
            self.log.info('Downloading {} has been canceled by the client.'.format(archive_filename))

        else:
            self.set_cookie("archiveToken", archive_token)
            self.log.info('Finished downloading {}.'.format(archive_filename))

        self.finish()