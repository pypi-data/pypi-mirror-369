"""Setup script for ML Assistant CLI."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version from __init__.py
version = {}
with open("mlcli/__init__.py") as fp:
    exec(fp.read(), version)

setup(
    name="ml-assistant-cli",
    version=version["__version__"],
    author="ML Assistant CLI Team",
    author_email="team@mlcli.dev",
    description="End-to-end ML workflow CLI - from dataset to deployed API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mlcli/mlcli",
    project_urls={
        "Bug Tracker": "https://github.com/mlcli/mlcli/issues",
        "Documentation": "https://mlcli.readthedocs.io",
        "Source Code": "https://github.com/mlcli/mlcli",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Console",
    ],
    python_requires=">=3.9",
    install_requires=[
        "typer[all]>=0.9.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
        "xgboost>=1.7.0",
        "bentoml>=1.2.0",
        "pyyaml>=6.0",
        "click>=8.0.0",
        "httpx>=0.24.0",
        "pathlib-mate>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "ruff>=0.1.0",
        ],
        "cloud": [
            "azure-ai-ml>=1.12.0",
            "azure-identity>=1.15.0",
            "boto3>=1.34.0",
            "sagemaker>=2.200.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mlcli=mlcli.main:cli_main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)