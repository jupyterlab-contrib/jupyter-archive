import platform
import shutil
import tarfile
import zipfile

import pytest


@pytest.mark.parametrize(
    "followSymlinks, download_hidden, file_list",
    [
        (
            False,
            False,
            {
                "download-archive-dir/test2.txt",
                "download-archive-dir/test1.txt",
                "download-archive-dir/test3.md",
            },
        ),
        (
            False,
            True,
            {
                "download-archive-dir/test2.txt",
                "download-archive-dir/test1.txt",
                "download-archive-dir/test3.md",
                "download-archive-dir/.test4.md",
                "download-archive-dir/.test-hidden-folder/test5.md",
            },
        ),
        (
            True,
            False,
            {
                "download-archive-dir/test2.txt",
                "download-archive-dir/test1.txt",
                "download-archive-dir/test3.md",
                "download-archive-dir/symlink-test-dir/test6.md",
            },
        ),
        (
            True,
            True,
            {
                "download-archive-dir/test2.txt",
                "download-archive-dir/test1.txt",
                "download-archive-dir/test3.md",
                "download-archive-dir/.test4.md",
                "download-archive-dir/.test-hidden-folder/test5.md",
                "download-archive-dir/symlink-test-dir/test6.md",
            },
        ),
    ],
)
@pytest.mark.parametrize(
    "format, mode",
    [
        ("zip", "r"),
        ("tgz", "r|gz"),
        ("tar.gz", "r|gz"),
        ("tbz", "r|bz2"),
        ("tbz2", "r|bz2"),
        ("tar.bz", "r|bz2"),
        ("tar.bz2", "r|bz2"),
        ("txz", "r|xz"),
        ("tar.xz", "r|xz"),
    ],
)
async def test_download(jp_fetch, jp_root_dir, followSymlinks, download_hidden, file_list, format, mode):
    if followSymlinks and platform.system() == "Windows":
        pytest.skip("Symlinks not working on Windows")

    # Create a dummy directory.
    archive_dir_path = jp_root_dir / "download-archive-dir"
    archive_dir_path.mkdir(parents=True)
    (archive_dir_path / "test1.txt").write_text("hello1")
    (archive_dir_path / "test2.txt").write_text("hello2")
    (archive_dir_path / "test3.md").write_text("hello3")
    (archive_dir_path / ".test4.md").write_text("hello4")

    hidden_folder = archive_dir_path / ".test-hidden-folder"
    hidden_folder.mkdir(parents=True)
    (hidden_folder / "test5.md").write_text("hello5")

    symlink_dir_path = jp_root_dir / "symlink-archive-dir"
    symlink_dir_path.mkdir(parents=True)
    (symlink_dir_path / "test6.md").write_text("hello6")
    if platform.system() != "Windows":
        (archive_dir_path / "symlink-test-dir").symlink_to(symlink_dir_path, target_is_directory=True)

    # Try to download the created folder.
    archive_relative_path = archive_dir_path.relative_to(jp_root_dir)
    params = {
        "archiveToken": 564646,
        "archiveFormat": format,
        "followSymlinks": str(followSymlinks).lower(),
        "downloadHidden": str(download_hidden).lower(),
    }
    r = await jp_fetch("directories", archive_dir_path.stem, params=params, method="GET")

    assert r.code == 200
    assert r.headers["content-type"] == "application/octet-stream"
    assert r.headers["cache-control"] == "no-cache"
    
    if format == "zip":
        with zipfile.ZipFile(r.buffer, mode=mode) as zf:
            assert set(zf.namelist()) == file_list
    else:
        with tarfile.open(fileobj=r.buffer, mode=mode) as tf:
            assert set(map(lambda m: m.name, tf.getmembers())) == file_list


@pytest.mark.parametrize(
    "format, mode",
    [
        ("zip", "w"),
        ("tgz", "w|gz"),
        ("tar.gz", "w|gz"),
        ("tbz", "w|bz2"),
        ("tbz2", "w|bz2"),
        ("tar.bz", "w|bz2"),
        ("tar.bz2", "w|bz2"),
        ("txz", "w|xz"),
        ("tar.xz", "w|xz"),
    ],
)
async def test_extract(jp_fetch, jp_root_dir, format, mode):
    # Create a dummy directory.
    archive_dir_path = jp_root_dir / "extract-archive-dir"
    archive_dir_path.mkdir(parents=True)

    (archive_dir_path / "extract-test1.txt").write_text("hello1")
    (archive_dir_path / "extract-test2.txt").write_text("hello2")
    (archive_dir_path / "extract-test3.md").write_text("hello3")

    # Make an archive
    archive_dir_path = jp_root_dir / "extract-archive-dir"
    archive_path = archive_dir_path.with_suffix("." + format)
    if format == "zip":
        with zipfile.ZipFile(archive_path, mode=mode) as writer:
            for file_path in archive_dir_path.rglob("*"):
                if file_path.is_file():
                    writer.write(file_path, file_path.relative_to(jp_root_dir))
    else:
        with tarfile.open(str(archive_path), mode=mode) as writer:
            for file_path in archive_dir_path.rglob("*"):
                if file_path.is_file():
                    writer.add(file_path, file_path.relative_to(jp_root_dir))

    # Remove the directory
    shutil.rmtree(archive_dir_path)

    r = await jp_fetch("extract-archive", archive_path.relative_to(jp_root_dir).as_posix(), method="GET")
    assert r.code == 200
    assert archive_dir_path.is_dir()

    n_files = len(list(archive_dir_path.glob("*")))
    assert n_files == 3
