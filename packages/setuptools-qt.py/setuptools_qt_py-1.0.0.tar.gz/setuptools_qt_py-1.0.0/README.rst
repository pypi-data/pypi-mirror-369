setuptools-Qt.py
================

.. image:: https://github.com/AWhetter/setuptools-qt.py/actions/workflows/main.yml/badge.svg?branch=main
    :target: https://github.com/AWhetter/setuptools-qt.py/actions/workflows/main.yml?query=branch%3Amain
    :alt: Github Build Status

.. image:: https://img.shields.io/pypi/v/setuptools-qt.py.svg
    :target: https://pypi.org/project/setuptools-qt.py/
    :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/setuptools-qt.py.svg
    :target: https://pypi.org/project/setuptools-qt.py/
    :alt: Supported Python Versions

A setuptools plugin for converting Qt .ui and .qrc files to Python files with Qt.py.


Installation
------------

``setuptools-qt.py`` can be installed through pip:

.. code-block:: bash

    pip install setuptools-qt.py

Usage
-----

Add ``setuptools-qt.py`` to the ``requires`` list in your project's ``pyproject.toml`` file.

.. code-block:: toml

    [build-system]
    requires = ["setuptools>=44.1", "setuptools-qt.py"]
    build-backend = "setuptools.build_meta"

The plugin will automatically find and compile ``.ui`` and ``.qrc`` file in your
packages' directories.
Compiled files are output with the same name as the source ``.ui`` or ``.qrc`` file,
with the file extension replaced with a suffix of ``_ui.py`` and ``_rc.py`` respectively.

.. code-block:: none

    myrepo
    └── src
        └── mypackage
            ├── myui.ui
            ├── myui_ui.py
            ├── myresources.ui
            ├── myresources_rc.py
            └── __init__.py

The output filename can be configured in the ``pyproject.toml`` file.

.. code-block:: toml

    [tool."setuptools-qt.py"]
    filename-ui = "{stem}.py"
    filename-qrc = "{stem}.py"

.. code-block:: none

    myrepo
    └── src
        └── mypackage
            ├── myui.ui
            ├── myui.py
            ├── myresources.ui
            ├── myrrsources.py
            └── __init__.py

Contributing
------------

Running the tests
~~~~~~~~~~~~~~~~~

Tests are executed through `tox <https://tox.readthedocs.io/en/latest/>`_.

.. code-block:: bash

    tox


Code Style
~~~~~~~~~~

Code is formatted using `ruff format <https://docs.astral.sh/ruff/formatter/>`_.

You can check your formatting using ruff's check mode:

.. code-block:: bash

    tox -e format

You can also get ruff to format your changes for you:

.. code-block:: bash

    .tox/format/bin/ruff format src/ tests/


Release Notes
~~~~~~~~~~~~~

Release notes are managed through `towncrier <https://towncrier.readthedocs.io/en/stable/index.html>`_.
When making a pull request you will need to create a news fragment to document your change:

.. code-block:: bash

    tox -e release_notes -- create --help


Versioning
----------

We use `SemVer <https://semver.org/>`_ for versioning.
For the versions available, see the `tags on this repository <https://github.com/AWhetter/setuptools-qt.py/tags>`_.


License
-------

This project is licensed under the MIT License.
See the `LICENSE.rst <LICENSE.rst>`_ file for details.
