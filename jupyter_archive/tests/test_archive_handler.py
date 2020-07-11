import io
import os
from os.path import join as pjoin
import pathlib
import shutil
import tarfile
import zipfile
import time

from nbformat import write
from notebook.tests.launchnotebook import NotebookTestBase
from traitlets.config import Config


class ArchiveHandlerTest(NotebookTestBase):

    config = Config({"NotebookApp": {"nbserver_extensions": {"jupyter_archive": True}}})

    def test_download(self):

        nbdir = self.notebook_dir

        # Create a dummy directory.
        archive_dir_path = pjoin(nbdir, "download-archive-dir")
        os.makedirs(archive_dir_path)
        with open(pjoin(archive_dir_path, "test1.txt"), "w") as f:
            f.write("hello1")
        with open(pjoin(archive_dir_path, "test2.txt"), "w") as f:
            f.write("hello2")
        with open(pjoin(archive_dir_path, "test3.md"), "w") as f:
            f.write("hello3")
        with open(pjoin(archive_dir_path, ".test4.md"), "w") as f:
            f.write("hello4")
        os.makedirs(pjoin(archive_dir_path, ".test-hidden-folder"))
        with open(pjoin(archive_dir_path, ".test-hidden-folder", "test5.md"), "w") as f:
            f.write("hello5")
        symlink_dir_path = pjoin(nbdir, "symlink-archive-dir")
        os.makedirs(symlink_dir_path)
        with open(pjoin(symlink_dir_path, "test6.md"), "w") as f:
            f.write("hello6")
        os.symlink(symlink_dir_path, pjoin(archive_dir_path, "symlink-test-dir"))

        # Try to download the created folder.
        archive_relative_path = os.path.basename(archive_dir_path)
        url_template = "directories/{}?archiveToken=564646&archiveFormat={}&followSymlinks={}&downloadHidden={}"

        file_lists = {
            "falsefalse": {
                "download-archive-dir/test2.txt",
                "download-archive-dir/test1.txt",
                "download-archive-dir/test3.md",
            },
            "falsetrue": {
                "download-archive-dir/test2.txt",
                "download-archive-dir/test1.txt",
                "download-archive-dir/test3.md",
                "download-archive-dir/.test4.md",
                "download-archive-dir/.test-hidden-folder/test5.md",
            },
            "truefalse": {
                "download-archive-dir/test2.txt",
                "download-archive-dir/test1.txt",
                "download-archive-dir/test3.md",
                "download-archive-dir/symlink-test-dir/test6.md"
            },
            "truetrue": {
                "download-archive-dir/test2.txt",
                "download-archive-dir/test1.txt",
                "download-archive-dir/test3.md",
                "download-archive-dir/.test4.md",
                "download-archive-dir/.test-hidden-folder/test5.md",
                "download-archive-dir/symlink-test-dir/test6.md"
            }
        }

        format_mode = {
            "zip": "r",
            "tgz": "r|gz",
            "tar.gz": "r|gz",
            "tbz": "r|bz2",
            "tbz2": "r|bz2",
            "tar.bz": "r|bz2",
            "tar.bz2": "r|bz2",
            "txz": "r|xz",
            "tar.xz": "r|xz",
        }

        for followSymlinks in ["true", "false"]:
            for download_hidden in ["true", "false"]:
                file_list = file_lists[followSymlinks + download_hidden]
                for format, mode in format_mode.items():
                    url = url_template.format(archive_relative_path, format, followSymlinks, download_hidden)
                    r = self.request("GET", url)
                    assert r.status_code == 200
                    assert r.headers["content-type"] == "application/octet-stream"
                    assert r.headers["cache-control"] == "no-cache"
                    if format == "zip":
                        with zipfile.ZipFile(io.BytesIO(r.content), mode=mode) as zf:
                            assert set(zf.namelist()) == file_list
                    else:
                        with tarfile.open(fileobj=io.BytesIO(r.content), mode=mode) as tf:
                            assert set(map(lambda m: m.name, tf.getmembers())) == file_list

    def test_extract(self):

        nbdir = self.notebook_dir

        # Create a dummy directory.
        archive_dir_path = pjoin(nbdir, "extract-archive-dir")
        os.makedirs(archive_dir_path)
        with open(pjoin(archive_dir_path, "extract-test1.txt"), "w") as f:
            f.write("hello1")
        with open(pjoin(archive_dir_path, "extract-test2.txt"), "w") as f:
            f.write("hello2")
        with open(pjoin(archive_dir_path, "extract-test3.md"), "w") as f:
            f.write("hello3")

        format_mode = {
            "zip": "w",
            "tgz": "w|gz",
            "tar.gz": "w|gz",
            "tbz": "w|bz2",
            "tbz2": "w|bz2",
            "tar.bz": "w|bz2",
            "tar.bz2": "w|bz2",
            "txz": "w|xz",
            "tar.xz": "w|xz",
        }

        for format, mode in format_mode.items():
            # Make an archive
            archive_dir_path = pathlib.Path(nbdir) / "extract-archive-dir"
            archive_path = archive_dir_path.with_suffix("." + format)
            if format == "zip":
                with zipfile.ZipFile(archive_path, mode=mode) as writer:
                    for file_path in archive_dir_path.rglob("*"):
                        if file_path.is_file():
                            writer.write(file_path, file_path.relative_to(nbdir))
            else:
                with tarfile.open(str(archive_path), mode=mode) as writer:
                    for file_path in archive_dir_path.rglob("*"):
                        if file_path.is_file():
                            writer.add(file_path, file_path.relative_to(nbdir))

            # Remove the directory
            shutil.rmtree(archive_dir_path)

            url_template = "extract-archive/{}"

            url = url_template.format(os.path.relpath(archive_path, nbdir))
            r = self.request("GET", url)
            assert r.status_code == 200
            assert archive_dir_path.is_dir()

            n_files = len(list(archive_dir_path.glob("*")))
            assert n_files == 3
