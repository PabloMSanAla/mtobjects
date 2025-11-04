#!/usr/bin/env python
from pathlib import Path
from setuptools import setup, find_packages

here = Path(__file__).parent

# Read the long description from README.rst
long_description = ""
readme = here / "README.rst"
if readme.exists():
    long_description = readme.read_text(encoding="utf-8")

setup(
    name="mtobjects",
    version="0.1.0",
    description="Max-tree based object detection and parameter extraction",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/CarolineHaigh/mtobjects",
    author="",
    license="MIT",
    packages=find_packages(exclude=("tests",)),
    py_modules=["mto"],
    include_package_data=True,
    package_data={
        # Ensure prebuilt shared objects are included in the package
        "mtolib": ["lib/*.so"],
    },
    install_requires=[
        "numpy",
        "astropy",
        "Pillow",
        "scikit-image",
        "astropy",
        "matplotlib",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
)
