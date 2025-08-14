"""Test that all the modules can be imported."""

import importlib
import pkgutil

import setuptools_qt_py


def test_can_import():
    """Test that all the modules can be imported."""
    package = setuptools_qt_py
    prefix = package.__name__ + "."
    for _, modname, _ in pkgutil.walk_packages(package.__path__, prefix):
        importlib.import_module(modname)
