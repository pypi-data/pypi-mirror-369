#!/usr/bin/env python3

"""Setup configuration for Signature package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
req_file = this_directory / "requirements.txt"
if req_file.exists():
    with open(req_file, "r", encoding="utf-8") as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#") and not line.startswith("-")
        ]

setup(
    name="litewave-ml-models-signature",
    version="0.0.10",  # This will be updated by the CI pipeline
    author="LitewaveAI",
    author_email="yash@litewave.ai",
    description="A package for signature verification and classification.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aiorch/litewave-ml-models/tree/main/signature",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "isort",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },
    include_package_data=True,
    package_data={
        "signature": [
            "*.yaml",
            "*.yml",
            "*.json",
        ],
    },
    zip_safe=False,
    keywords="signature verification classification machine-learning computer-vision pytorch",
) 