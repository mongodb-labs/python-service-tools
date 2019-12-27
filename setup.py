#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""Setup script for miscutils."""
from __future__ import absolute_import
from __future__ import print_function

from glob import glob
import os
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def _find_version_line_in_file(file_path: str) -> str:
    with open(str(file_path), "r") as fileh:
        version_lines = [line for line in fileh.readlines() if line.startswith("VERSION")]
        if len(version_lines) != 1:
            raise ValueError(f"Unable to determine 'VERSION' in {file_path}")
        return version_lines[0]


def _lookup_local_module_version(file_path: str) -> str:
    path_to_init = os.path.join(str(file_path), "__init__.py")
    version_tuple = eval(_find_version_line_in_file(path_to_init).split("=")[-1])
    return ".".join([str(x) for x in version_tuple])


version = _lookup_local_module_version(os.path.join(os.path.dirname(__file__), "src", "miscutils"))


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="misc-utils-py",
    version=version,
    license="Apache License, Version 2.0",
    description="Misc utilities for python projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="David Bradford",
    author_email="david.bradford@mongodb.com",
    url="https://github.com/dbradf/misc-utils-py",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    install_requires=[
        "pylibversion >= 0.1",
        "python-json-logger >= 0.1",
        "structlog >= 19"
    ],
    entry_points={"console_scripts": []},
)
