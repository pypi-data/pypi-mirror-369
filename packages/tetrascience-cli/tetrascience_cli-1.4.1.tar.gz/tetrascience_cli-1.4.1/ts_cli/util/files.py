import os
import shutil
from pathlib import Path
from typing import List, Union


def copy(*, src, dst):
    """
    :param src:
    :param dst:
    :return:
    """

    src_path = Path(src)
    dst_path = Path(dst)
    if src_path.is_dir():
        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
    else:
        os.makedirs(dst_path.parent, exist_ok=True)
        shutil.copy(src_path, dst_path)


def get_conflicts(*, src, dst, preserve_templates: bool) -> List[Path]:
    dst = Path(dst)
    if not dst.exists():
        return []
    if not dst.is_dir():
        return [dst]
    conflicts = []
    for root, folders, files in os.walk(src, topdown=True):
        for folder in folders:
            path = Path(os.path.join(dst, folder))
            if path.exists() and not path.is_dir():
                conflicts.append(path)
        for file in files:
            path = Path(os.path.join(dst, file))
            if file.endswith(".template"):
                if preserve_templates and path.exists():
                    conflicts.append(path)
                path = path.with_name(path.stem)
            if path.exists():
                conflicts.append(path)
    return conflicts


def delete(*files: Union[Path, str]):
    for file in files:
        path = Path(file)
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)
