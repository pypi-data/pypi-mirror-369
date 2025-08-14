"""Module for file operations used in the ARI3D project."""
import errno
import os
import shutil
import stat
import sys
from pathlib import Path

import yaml

enc = sys.getfilesystemencoding()


def get_dict_from_yml(yml_file):
    """Read a dictionary from a file in yml format."""
    with open(yml_file) as yml_f:
        d = yaml.safe_load(yml_f)

    if not isinstance(d, dict):
        raise TypeError("Yaml file %s invalid!" % str(yml_file))

    return d


def write_dict_to_yml(yml_file, d):
    """Write a dictionary to a file in yml format."""
    yml_file = Path(yml_file)
    create_path_recursively(yml_file.parent)

    with open(yml_file, "w+") as yml_f:
        yml_f.write(yaml.dump(d, Dumper=yaml.Dumper))

    return True


def create_path_recursively(path):
    """Create a path. Creates missing parent folders."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)

    return True


def copy_folder(folder_to_copy, destination, copy_root_folder=True, force_copy=False):
    """Copy a folder to a destination.

    Args:
        folder_to_copy:
            The folder to copy
        destination:
            The destination folder to copy to
        copy_root_folder:
            boolean value. if true copies the root folder in the target destination.
            Else all files in the folder to copy.
        force_copy:
            boolean value. If true, removes the destination folder before copying.

    """
    folder_to_copy = Path(folder_to_copy)
    destination = Path(destination)

    if os.path.exists(destination) and os.path.samefile(folder_to_copy, destination):
        return destination

    if copy_root_folder:
        destination = destination.joinpath(folder_to_copy.name)

    if force_copy:
        force_remove(destination)

    create_path_recursively(destination)

    for root, dirs, files in os.walk(folder_to_copy):
        root = Path(root)

        for d in dirs:
            copy_folder(
                root.joinpath(d), destination.joinpath(d), copy_root_folder=False
            )
        for fi in files:
            copy(root.joinpath(fi), destination)
        break

    return destination


def copy(file, path_to) -> Path:
    """Copy a file A to either folder B or file B. Makes sure folder structure for target exists."""
    file = Path(file)
    path_to = Path(path_to)

    if os.path.exists(path_to) and os.path.samefile(file, path_to):
        return path_to

    create_path_recursively(path_to.parent)

    return Path(shutil.copy(file, path_to))


def force_remove(path, warning=True):
    """Force remove a file or folder. If the path is read-only, it will be made writable first."""
    path = Path(path)
    if path.exists():
        try:
            if path.is_file():
                try:
                    path.unlink()
                except PermissionError:
                    handle_remove_readonly(os.unlink, path, sys.exc_info())
            else:
                shutil.rmtree(
                    str(path), ignore_errors=False, onerror=handle_remove_readonly
                )
        except PermissionError as e:
            if not warning:
                raise e


def handle_remove_readonly(func, path, exc):
    """Change readonly flag of a given path."""
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise
