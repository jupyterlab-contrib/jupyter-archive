import io
import os
import pathlib
import shutil
import zipfile
import time

from nbformat import write
from notebook.tests.launchnotebook import NotebookTestBase
from traitlets.config import Config

pjoin = os.path.join


class ArchiveHandlerTest(NotebookTestBase):

  config = Config({'NotebookApp': {"nbserver_extensions": {"jupyter_archive": True}}})

  def test_download(self):

    nbdir = self.notebook_dir

    # Create a dummy directory.
    archive_dir_path = pjoin(nbdir, 'download-archive-dir')
    os.makedirs(archive_dir_path)
    with open(pjoin(archive_dir_path, 'test1.txt'), 'w') as f:
        f.write('hello1')
    with open(pjoin(archive_dir_path, 'test2.txt'), 'w') as f:
        f.write('hello2')
    with open(pjoin(archive_dir_path, 'test3.md'), 'w') as f:
        f.write('hello3')

    # Try to download the created folder.
    archive_relative_path = os.path.basename(archive_dir_path)
    url_template = 'directories/{}?archiveToken=564646&archiveFormat={}'

    url = url_template.format(archive_relative_path, 'zip')
    r = self.request('GET', url)
    assert r.status_code == 200
    assert r.headers['content-type'] == 'application/octet-stream'
    assert r.headers['cache-control'] == 'no-cache'

    url = url_template.format(archive_relative_path, 'tgz')
    r = self.request('GET', url)
    assert r.status_code == 200
    assert r.headers['content-type'] == 'application/octet-stream'
    assert r.headers['cache-control'] == 'no-cache'

    url = url_template.format(archive_relative_path, 'tbz')
    r = self.request('GET', url)
    assert r.status_code == 200
    assert r.headers['content-type'] == 'application/octet-stream'
    assert r.headers['cache-control'] == 'no-cache'

    url = url_template.format(archive_relative_path, 'txz')
    r = self.request('GET', url)
    assert r.status_code == 200
    assert r.headers['content-type'] == 'application/octet-stream'
    assert r.headers['cache-control'] == 'no-cache'

  def test_extract(self):

    nbdir = self.notebook_dir

    # Create a dummy directory.
    archive_dir_path = pjoin(nbdir, 'extract-archive-dir')
    archive_dir_path = pjoin(archive_dir_path, 'extract-archive-dir')
    os.makedirs(archive_dir_path)
    with open(pjoin(archive_dir_path, 'extract-test1.txt'), 'w') as f:
        f.write('hello1')
    with open(pjoin(archive_dir_path, 'extract-test2.txt'), 'w') as f:
        f.write('hello2')
    with open(pjoin(archive_dir_path, 'extract-test3.md'), 'w') as f:
        f.write('hello3')

    # Make an archive
    archive_dir_path = pathlib.Path(archive_dir_path).parent
    archive_path = archive_dir_path.with_suffix(".zip")
    with zipfile.ZipFile(archive_path, mode='w') as writer:
        for file_path in archive_dir_path.rglob("*"):
          if file_path.is_file():
            writer.write(file_path, file_path.relative_to(archive_dir_path))

    # Remove the directory
    shutil.rmtree(archive_dir_path)

    url_template = 'extract-archive/{}'

    url = url_template.format(archive_path)
    r = self.request('GET', url)
    assert r.status_code == 200

    time.sleep(0.5)

    assert archive_dir_path.is_dir()

    n_files = len(list(archive_dir_path.glob("*")))
    assert n_files == 3
