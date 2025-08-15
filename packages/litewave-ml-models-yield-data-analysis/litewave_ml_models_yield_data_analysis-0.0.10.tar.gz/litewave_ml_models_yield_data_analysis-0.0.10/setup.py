#!/usr/bin/env python3

"""Setup configuration for MVA Pipeline package."""

from pathlib import Path

from setuptools import find_packages, setup

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
    name="litewave-ml-models-yield-data-analysis",
    version="0.0.10",
    author="LitewaveAI",
    author_email="yash@litewave.ai",
    description="Multivariate analytics pipeline for manufacturing yield optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aiorch/litewave-ml-models/tree/main/yield_data_analysis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Manufacturing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Chemistry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
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
    entry_points={
        "console_scripts": [
            "mva-pipeline=mva_pipeline.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mva_pipeline": [
            "config.yaml",
            "*.yaml",
            "*.yml",
        ],
    },
    zip_safe=False,
    keywords="manufacturing analytics pca shap anomaly-detection yield-optimization pharmaceutical",
)
