from __future__ import annotations

import importlib
import runpy
import subprocess
import sys
from pathlib import Path


class PoetryAdapter:
    """
    A class to handle running scripts within a Poetry-managed project environment.
    """

    @staticmethod
    def run_script(launcher: Path | str, arguments: list) -> None:
        """
        Run a script within a Poetry-managed project environment.

        :param launcher: The path to the launcher script.
        :type launcher: Path
        :param arguments: List of arguments to pass to the script.
        :type arguments: list[str]
        :return: None
        """
        pkg_name = Path(launcher).stem.replace("-", "_")
        pkg_src = Path(launcher, "../../src/", pkg_name).resolve()
        sys.path.insert(0, str(pkg_src))
        venv_activator = PoetryAdapter.get_activator_path(pkg_src)

        if venv_activator.is_file():
            # Activate package's virtual environment
            runpy.run_path(str(venv_activator))

            launcher_module = importlib.import_module(f"{pkg_name}.cli")
            launcher_module.cli(arguments)
        else:
            print(
                f"Script preparation failed. Make sure `poetry install` can complete successfully in {pkg_src}.",
            )

    @staticmethod
    def update_script(launcher: Path) -> None:
        pkg_name = Path(launcher).stem.replace("-", "_")
        pkg_src = Path(launcher, "../../src/", pkg_name).resolve()

        sys.path.insert(0, str(pkg_src))
        subprocess.run(  # noqa: S603
            ["poetry", "--directory", pkg_src, "install"],  # noqa: S607
            capture_output=True,
            check=False,
        )
        subprocess.run(  # noqa: S603
            ["poetry", "--directory", pkg_src, "update"],  # noqa: S607
            capture_output=True,
            check=False,
        )

    @staticmethod
    def get_activator_path(directory: Path) -> Path:
        """
        Get the path to the virtual environment activator script.

        :param directory: The directory of the Poetry project.
        :type directory: Path
        :return: The path to the activator script, or the current working directory if not found.
        :rtype: Path
        """
        venv_dir_stdout = subprocess.run(  # noqa: S603
            ["poetry", "--directory", directory, "env", "info", "--path"],  # noqa: S607
            stdout=subprocess.PIPE,
            check=False,
        )
        venv_dir = Path(venv_dir_stdout.stdout.decode("utf-8").strip())
        activator_posix = Path(venv_dir, "bin", "activate_this.py")
        activator_win = Path(venv_dir, "Scripts", "activate_this.py")

        if activator_posix.is_file():
            return activator_posix

        if activator_win.is_file():
            return activator_win

        return Path.cwd()
