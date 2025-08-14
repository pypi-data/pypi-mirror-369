#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Based on https://github.com/pypa/sampleproject/blob/master/setup.py."""
import codecs
import io
import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

HERE = os.path.abspath(os.path.dirname(__file__))


def parse_reqs(req_path="./requirements.txt"):
    """Parse lib requirements from requirement.txt file"""
    install_requires = []
    with io.open(os.path.join(HERE, "requirements.txt"), encoding="utf-8") as handle:
        # remove comments and empty lines
        lines = (line.strip() for line in handle if line.strip() and not line.startswith("#"))

        for line in lines:
            # add the line as a new requirement
            install_requires.append(line)

    return install_requires


REQUIRED = parse_reqs()


# shortcut for building/publishing to Pypi
if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()


# this is a plug-in for setuptools that will invoke py.test
class PyTest(TestCommand):

    """Set up the py.test test runner."""

    user_options = [("pytest-args=", "a", "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        """Set options for the command line."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Execute the test runner command."""
        # import here, because outside the required eggs aren't loaded yet
        import pytest

        sys.exit(pytest.main(self.test_args))


# get the long description from the relevant file
with codecs.open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()


setup(
    name="chanjo-report",
    # versions should comply with PEP440
    version="4.11.5",
    description="Automatically render coverage reports from Chanjo ouput",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    # what does your project relate to?
    keywords="chanjo-report development",
    author="Robin Andeer",
    author_email="robin.andeer@scilifelab.se",
    license="MIT",
    # the project's main homepage
    url="https://github.com/robinandeer/chanjo-report",
    packages=find_packages(exclude=("tests*", "docs", "examples")),
    # if there are data files included in your packages
    include_package_data=True,
    package_data={
        "chanjo_report": [
            "server/blueprints/report/static/*.css",
            "server/blueprints/report/static/vendor/*.css",
            "server/blueprints/report/templates/report/*.html",
            "server/blueprints/report/templates/report/layouts/*.html",
            "server/blueprints/report/templates/report/components/*.html",
            "server/translations/sv/LC_MESSAGES/*",
        ]
    },
    zip_safe=False,
    install_requires=REQUIRED,
    tests_require=["pytest"],
    cmdclass={"test": PyTest},
    # to provide executable scripts, use entry points
    entry_points={
        "chanjo.subcommands.4": ["report = chanjo_report.cli:report"],
    },
    # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Environment :: Console",
    ],
)
