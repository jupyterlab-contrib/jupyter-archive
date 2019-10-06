import os
import asyncio
import zipfile
import tarfile
import pathlib
import threading

from tornado import gen, web, iostream
from notebook.base.handlers import IPythonHandler


class ArchiveStream():
  def __init__(self, handler):
    self.handler = handler
    self.position = 0

  def write(self, data):
    self.position += len(data)
    self.handler.write(data)
    del data

  def tell(self):
    return self.position

  def flush(self):
    self.handler.flush()


def make_writer(handler, archive_format="zip"):
  fileobj = ArchiveStream(handler)

  if archive_format == "zip":
    archive_file = zipfile.ZipFile(fileobj, mode='w')
    archive_file.add = archive_file.write
  elif archive_format in ["tgz", "tar.gz"]:
    archive_file = tarfile.open(fileobj=fileobj, mode='w|gz')
  elif archive_format in ["tbz", "tbz2", "tar.bz", "tar.bz2"]:
    archive_file = tarfile.open(fileobj=fileobj, mode='w|bz2')
  elif archive_format in ["txz", "tar.xz"]:
    archive_file = tarfile.open(fileobj=fileobj, mode='w|xz')
  else:
    raise ValueError("'{}' is not a valid archive format.".format(archive_format))
  return archive_file


def make_reader(archive_path):

  archive_format = archive_path.suffix[1:]

  if archive_format == "zip":
    archive_file = zipfile.ZipFile(archive_path, mode='r')
  elif archive_format in ["tgz", "tar.gz"]:
    archive_file = tarfile.open(archive_path, mode='r|gz')
  elif archive_format in ["tbz", "tbz2", "tar.bz", "tar.bz2"]:
    archive_file = tarfile.open(archive_path, mode='r|bz2')
  elif archive_format in ["txz", "tar.xz"]:
    archive_file = tarfile.open(archive_path, mode='r|xz')
  else:
    raise ValueError("'{}' is not a valid archive format.".format(archive_format))
  return archive_file


class DownloadArchiveHandler(IPythonHandler):

  @web.authenticated
  @gen.coroutine
  def get(self, archive_path, include_body=False):

    # /directories/ requests must originate from the same site
    self.check_xsrf_cookie()
    cm = self.contents_manager

    if cm.is_hidden(archive_path) and not cm.allow_hidden:
        self.log.info("Refusing to serve hidden file, via 404 Error")
        raise web.HTTPError(404)

    archive_token = self.get_argument('archiveToken')
    archive_format = self.get_argument('archiveFormat', 'zip')

    task = asyncio.ensure_future(self.archive_and_download(archive_path, archive_format, archive_token))

    try:
      yield from task
    except asyncio.CancelledError:
      task.cancel()

  @gen.coroutine
  def archive_and_download(self, archive_path, archive_format, archive_token):

    archive_path = pathlib.Path(archive_path)
    archive_name = archive_path.name
    archive_filename = archive_path.with_suffix(".{}".format(archive_format)).name

    # We gonna send out event streams!
    self.set_header('content-type', 'application/octet-stream')
    self.set_header('cache-control', 'no-cache')
    self.set_header('content-disposition',
                    'attachment; filename={}'.format(archive_filename))

    try:
      self.log.info('Prepare {} for archiving and downloading.'.format(archive_filename))
      archive_writer = make_writer(self, archive_format)

      with archive_writer as writer:
        for file_path in archive_path.rglob("*"):
          if file_path.is_file():
            writer.add(file_path, file_path.relative_to(archive_path))
            yield from self.flush()

    except iostream.StreamClosedError:
      self.log.info('Downloading {} has been canceled by the client.'.format(archive_filename))
      del writer
      raise asyncio.CancelledError

    else:
      self.set_cookie("archiveToken", archive_token)
      self.log.info('Finished downloading {}.'.format(archive_filename))


class ExtractArchiveHandler(IPythonHandler):

  @web.authenticated
  def get(self, archive_path, include_body=False):

    # /extract-archive/ requests must originate from the same site
    self.check_xsrf_cookie()
    cm = self.contents_manager

    if cm.is_hidden(archive_path) and not cm.allow_hidden:
        self.log.info("Refusing to serve hidden file, via 404 Error")
        raise web.HTTPError(404)

    archive_path = pathlib.Path(archive_path).absolute()
    archive_name = archive_path.name

    # Run it in a thread so it's not blocking.
    # TODO: Convert to async ideally.
    run_task = lambda : self.extract_archive(archive_path)
    threading.Thread(target=run_task).start()

  def extract_archive(self, archive_path):

      archive_destination = archive_path.parent
      self.log.info('Begin extraction of {} to {}.'.format(archive_path, archive_destination))

      archive_reader = make_reader(archive_path)
      with archive_reader as archive:
        archive.extractall(archive_destination)

      self.log.info('Finished extracting {} to {}.'.format(archive_path, archive_destination))
