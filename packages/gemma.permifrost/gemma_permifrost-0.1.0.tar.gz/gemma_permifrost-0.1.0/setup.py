#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION") as version_file:
    version = version_file.read().strip()

requires = [
    "cerberus",
    "colorama",
    "coloredlogs",
    "click",
    "click-default-group",
    "pyyaml",
    "snowflake-connector-python[secure-local-storage]",
    "snowflake-sqlalchemy==1.5.3",
    "sqlalchemy",
]

dev_requires = [
    "black",
    "bumpversion",
    "changelog-cli",
    "coverage",
    "flake8",
    "isort",
    "mypy",
    "pre-commit",
    "pytest",
    "pytest-cov",
    "pytest-mock",
    "types-PyYAML",
]

setup(
    name="gemma.permifrost",
    version=version,
    author="Gemma Analytics",
    author_email="info@gemmaanalytics.com",
    description="Permifrost Permissions - Fork by Gemma Analytics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gemma-Analytics/permifrost",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    py_modules=["permifrost"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    setup_requires=["pytest-runner"],
    tests_require=dev_requires,
    # run `make requirements.txt` after editing
    install_requires=requires,
    extras_require={"dev": dev_requires},
    entry_points={"console_scripts": ["permifrost = permifrost.cli:main"]},
)
