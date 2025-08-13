"""Setup configuration for HiLink API package."""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define requirements directly instead of reading from file
requirements = [
    "requests>=2.31.0",
    "xmltodict>=0.13.0",
    "beautifulsoup4>=4.12.0",
    "urllib3>=2.0.0",
]

setup(
    name="hilinkapi",
    version="2.0.0",
    author="HiLink API Contributors",
    author_email="",
    description="Modern Python API for Huawei HiLink modems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hilinkapi",
    py_modules=["HiLinkAPI"],  # Specify the main module
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    license="MIT",  # Use license field instead of classifier
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-autodoc-typehints>=1.19.0",
        ]
    },
    include_package_data=True,
)