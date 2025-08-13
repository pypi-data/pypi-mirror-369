#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

from cidc_schemas import __author__, __email__, __version__

setup(
    author=__author__,
    author_email=__email__,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
    ],
    description="The CIDC data model and tools for working with it.",
    python_requires=">=3.9,<3.11",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="cidc_schemas",
    name="nci_cidc_schemas",
    packages=find_packages(include=["cidc_schemas", "cidc_schemas.prism"]),
    test_suite="tests",
    url="https://github.com/NCI-CIDC/cidc-schemas",
    version=__version__,
    zip_safe=False,
    entry_points={"console_scripts": ["cidc_schemas=cidc_schemas.cli:main"]},
)
