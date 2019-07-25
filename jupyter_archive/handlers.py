import os
import zipfile

from tornado import gen, web
from notebook.base.handlers import IPythonHandler


class ZipStream():
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


def make_writer(fileobj, archive_format="zip"):
    # TODO: add suport for .tar.gz format.
    if archive_format == "zip":
        zip_file = zipfile.ZipFile(fileobj, mode='w')
        zip_file.add = zip_file.write
    else:
        raise ValueError(f"'{archive_format}' is not a valid archive format.")
    return zip_file


class ZipHandler(IPythonHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @web.authenticated
    @gen.coroutine
    def get(self):
        zip_path = self.get_argument('zipPath')
        zip_token = self.get_argument('zipToken')
        archive_format = self.get_argument('format', 'zip')

        # We gonna send out event streams!
        self.set_header('content-type', 'application/octet-stream')
        self.set_header('cache-control', 'no-cache')
        self.set_header(
            'content-disposition',
            'attachment; filename=\"{}.{}\"'.format(zip_path or 'home', fmt)
        )

        if zip_path == '':
            zip_path = '.'

        self.log.info('zipping')

        file_name = None
        archive_writer = make_writer(ZipStream(self), archive_format)
        with archive_writer as writer:
            for root, dirs, files in os.walk(zip_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    self.log.info("{}\n".format(file_path))
                    writer.add(file_path, os.path.join(root[len(zip_path):], file_))

        self.set_cookie("zipToken", zip_token)
        self.log.info('Finished zipping')
