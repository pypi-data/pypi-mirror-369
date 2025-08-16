#!/usr/bin/env python
import os
from setuptools import setup, find_packages

# Get the directory where setup.py is located
here = os.path.abspath(os.path.dirname(__file__))

# Read requirements from requirements.txt
requirements_path = os.path.join(here, "requirements.txt")
with open(requirements_path, "r") as file:
    requirements = file.read().splitlines()

setup(
    name="rate-limiter-modern-py",
    version="0.4.0",
    description="Rate-limiter module which leverages DynamoDB to enforce resource limits. Revived from LifeOmic's original implementation. With support for Python 3.9+, and updated dependencies.",
    keywords=["lifeomic", "dynamodb", "rate", "limit"],
    author="Matthew Tieman",
    author_email="mjtieman55@gmail.com",
    url="https://github.com/lifeomic/rate-limiter-modern-py",
    download_url="https://github.com/lifeomic/rate-limiter-modern-py/archive/0.4.0.tar.gz",
    packages=find_packages(),
    license="MIT",
    python_requires=">=3.9.0",
    install_requires=requirements,
)
