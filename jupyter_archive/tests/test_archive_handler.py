from ipython_genutils import py3compat
from notebook.tests.launchnotebook import NotebookTestBase
from notebook.utils import url_path_join
from nbformat.v4 import (new_notebook,
                         new_markdown_cell, new_code_cell,
                         new_output)
from nbformat import write
import requests
import io
import os
import logging
import tempfile
import json
import unittest
from unicodedata import normalize

from traitlets.config import Config

pjoin = os.path.join


class ArchiveHandlerTest(NotebookTestBase):

  config = Config({'NotebookApp': {"nbserver_extensions": {"jupyter_archive": True}}})

  def test_download(self):

    nbdir = self.notebook_dir

    # Create a dummy directory.
    archive_dir_path = pjoin(nbdir, 'archive-dir')
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
