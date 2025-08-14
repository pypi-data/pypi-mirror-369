"""Setuptools extension for compiling .ui and .qrc files with Qt.py."""

from __future__ import annotations

from collections.abc import Iterable
import glob
import logging
import os
import shlex
import subprocess
import sys
from typing import Any, ClassVar

import Qt.QtCompat
from setuptools import Command
from setuptools.dist import Distribution
from setuptools.errors import ExecError

__version__ = "1.0.0"


class build_qt_py(Command):
    """Build .ui and .qrc files."""

    description = "build .ui and .qrc files with Qt.py"
    user_options: ClassVar[list[tuple[str, str | None, str]]] = [
        ("filename-qrc", None, "Output filename template for .qrc files"),
        ("filename-ui", None, "Output filename template for .ui files"),
    ]

    def initialize_options(self) -> None:
        """Initialize options for the build_qt_py command."""
        self.filename_templates = {
            "qrc": getattr(self.distribution, "filename_qrc", None) or "{stem}_rc.py",
            "ui": getattr(self.distribution, "filename_ui", None) or "{stem}_ui.py",
        }

        build_cmd = self.distribution.get_command_obj("build_py")
        build_cmd.initialize_options()

    def finalize_options(self) -> None:
        """Finalize options for the build_qt_py command."""
        build_cmd = self.distribution.get_command_obj("build_py")
        build_cmd.finalize_options()

    def run(self) -> None:
        """Execute the build_qt_py command.

        Compiles all found .ui and .qrc files in the distribution's package directories.
        Only recompiles if the source .ui or .qrc file is newer than the output.

        Raises:
            ExecError: If uic or rcc returns a non-zero exit code.
        """
        for source_file, output_file in self._get_files():
            self._compile_file(source_file, output_file)

    def _compile_file(self, in_file: str, out_file: str) -> None:
        source_mtime = os.path.getmtime(in_file)
        try:
            output_mtime = os.path.getmtime(out_file)
        except FileNotFoundError:
            pass
        else:
            if output_mtime >= source_mtime:
                return

        if os.path.splitext(in_file)[1] == ".ui":
            cmd = ["uic", "--generator", "python", in_file]
        else:
            cmd = ["rcc", "--generator", "python", in_file]

        if sys.version_info >= (3, 8):
            cmd_str = shlex.join(cmd)
        else:
            cmd_str = " ".join(cmd)
        self.announce(f"Running command: {cmd_str}", level=logging.INFO)

        try:
            pyside_out = subprocess.check_output(cmd, text=True)
        except subprocess.CalledProcessError as e:
            raise ExecError(f"error running {cmd[0]}: {e.returncode}")

        with open(out_file, "w") as out_f:
            out_f.writelines(Qt.QtCompat._convert(pyside_out.splitlines()))  # type: ignore[attr-defined]

    def _get_files(self) -> Iterable[tuple[str, str]]:
        build_cmd = self.distribution.get_command_obj("build_py")
        for package in self.distribution.packages:
            package_dir = build_cmd.get_package_dir(package)
            for file_type, filename_template in self.filename_templates.items():
                glob_pattern = f"*.{file_type}"
                for source_file in glob.glob(os.path.join(package_dir, glob_pattern)):
                    package_dir, filename = os.path.split(source_file)
                    output_filename = filename_template.format(
                        stem=os.path.splitext(filename)[0]
                    )
                    output_file = os.path.join(package_dir, output_filename)
                    yield (source_file, output_file)

    def get_source_files(self) -> list[str]:
        """Return the list of source .ui and .qrc files.

        Returns:
            list[str]: List of paths to .ui and .qrc files.
        """
        return list(x[0] for x in self._get_files())

    def get_outputs(self) -> list[str]:
        """Return the list of output files for the command."""
        return list(x[1] for x in self._get_files())


def load_pyproject_config(dist: Distribution, cfg: dict[str, Any]) -> None:
    """Load setuptools-qt_py configuration from pyproject.toml.

    Args:
        dist: The setuptools Distribution instance.
        cfg: Configuration dictionary from pyproject.toml.
    """
    dist.filename_qrc = cfg.get("filename-qrc")  # type: ignore[attr-defined]
    dist.filename_ui = cfg.get("filename-ui")  # type: ignore[attr-defined]


def pyprojecttoml_config(dist: Distribution) -> None:
    """Configure the distribution from pyproject.toml.

    Registers the build_qt_py command and loads
    configuration from pyproject.toml if present.

    Args:
        dist: The setuptools Distribution instance.
    """
    build = dist.get_command_class("build")
    build.sub_commands.insert(0, ("build_qt_py", (lambda cmd: True)))

    if sys.version_info[:2] >= (3, 11):
        from tomllib import load as toml_load
    else:
        from tomli import load as toml_load
    try:
        with open("pyproject.toml", "rb") as f:
            cfg = toml_load(f).get("tool", {}).get("setuptools-qt.py")
    except FileNotFoundError:
        pass
    else:
        if cfg:
            load_pyproject_config(dist, cfg)
