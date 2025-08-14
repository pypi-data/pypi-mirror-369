import logging
from pathlib import Path


def remove_empty_directories(directory: Path) -> None:
    """
    Remove empty directories in the given directory.

    :param directory: Path to the directory to process
    :type directory: :class:`Path`
    :return: None. The function modifies the <directory> in place.
    """
    for dir_path in sorted(directory.rglob("*"), reverse=True):
        if dir_path.is_dir() and not any(dir_path.iterdir()):
            dir_path.rmdir()
            logging.info("Removed empty directory %s", dir_path)
