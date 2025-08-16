import io
import os
import zipfile
from pathlib import Path
from typing import Iterable, Union

from ts_cli.util.files import copy


def abs_path_relative_to(relative_path, relative_to):
    """
    Join the two paths, and then provide the absolute path
    :param relative_path:
    :param relative_to:
    :return:
    """
    return os.path.abspath(
        Path(
            Path(relative_to).expanduser(),
            Path(relative_path).expanduser(),
        )
    )


def some_match(path, patterns, relative_to):
    """
    Returns true if there is some pattern that points to the same path as `path`
    :param path:
    :param patterns:
    :param relative_to:
    :return:
    """
    absolute_path = abs_path_relative_to(relative_to=relative_to, relative_path=path)
    matches = map(
        lambda pattern: absolute_path
        == abs_path_relative_to(relative_path=pattern, relative_to=relative_to),
        patterns,
    )
    return any(matches)


def included(path, *, inclusions, exclusions, relative_to):
    """
    Return true if file is not excluded or is explicitly included
    :param path:
    :param inclusions:
    :param exclusions:
    :param relative_to:
    :return:
    """
    return (not some_match(path, exclusions, relative_to)) or some_match(
        path, inclusions, relative_to
    )


def iterate_directory_inclusions(
    path: Union[str, Path],
    *,
    exclusions: Iterable[str],
    inclusions: Iterable[str],
):
    """
    Yields the relative file path for every file that is included
    :param path:
    :param exclusions:
    :param inclusions:
    :return:
    """
    if included(".", inclusions=inclusions, exclusions=exclusions, relative_to=path):
        for root, folders, files in os.walk(path, topdown=True):
            removals = set()
            for folder in folders:
                local_path = os.path.join(root, folder)
                relative_path = os.path.relpath(local_path, path)
                if not included(
                    relative_path,
                    inclusions=inclusions,
                    exclusions=exclusions,
                    relative_to=path,
                ):
                    removals.add(folder)
            for removal in removals:
                folders.remove(removal)

            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, os.path.join(path))
                if included(
                    relative_path,
                    inclusions=inclusions,
                    exclusions=exclusions,
                    relative_to=path,
                ):
                    yield relative_path


def copy_included_files_to(
    *,
    src_dir: str,
    dst_dir: str,
    exclusions: Iterable[str],
    inclusions: Iterable[str],
):
    """
    Copies the included files from `src_dir` to `dst_dir`
    :param src_dir:
    :param dst_dir:
    :param exclusions:
    :param inclusions:
    :return:
    """
    for relative_path in iterate_directory_inclusions(
        path=src_dir, exclusions=exclusions, inclusions=inclusions
    ):
        copy(src=Path(src_dir, relative_path), dst=Path(dst_dir, relative_path))


def add_directory_to_archive(
    zip_archive: zipfile.ZipFile,
    path: Union[str, Path],
) -> zipfile.ZipFile:
    """
    Copies all files under `path` to the archive
    :param zip_archive:
    :param path:
    :return:
    """
    for root, _folders, files in os.walk(path, topdown=True):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, os.path.join(path))
            zip_archive.write(local_path, relative_path)
    return zip_archive


def compress_directory(directory: Union[str, Path]):
    """
    Adds the directory to a zip file, and return the zip file's bytes
    :param directory:
    :return:
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, True) as zip_archive:
        add_directory_to_archive(
            zip_archive,
            directory,
        )
    return zip_buffer.getvalue()
