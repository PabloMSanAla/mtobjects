#!/usr/bin/env python
import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install


class CustomBuildExt(build_ext):
    """Custom build_ext command to compile C extensions using recompile.sh"""
    
    def run(self):
        # Run the recompile.sh script
        script_path = os.path.join(os.path.dirname(__file__), "recompile.sh")
        if os.path.exists(script_path):
            try:
                subprocess.check_call(["bash", str(script_path)])
                print("Successfully compiled C extensions using recompile.sh")
            except subprocess.CalledProcessError as e:
                print(f"Error running recompile.sh: {e}")
                raise
        else:
            print("Warning: recompile.sh not found, skipping C extension compilation")
        
        # Call parent implementation
        super().run()


class CustomInstall(install):
    """Custom install command to ensure C extensions are built"""
    
    def run(self):
        # Run build_ext before install
        self.run_command('build_ext')
        super().run()


here = os.path.dirname(__file__)

# Read the long description from README.rst
long_description = ""
readme = os.path.join(here, "README.rst")
if os.path.exists(readme):
    with open(readme, encoding="utf-8") as f:
        long_description = f.read()

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
        # Include compiled shared objects and source files
        "mtolib": ["lib/*.so", "src/*.c", "src/*.h"],
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
    cmdclass={
        'build_ext': CustomBuildExt,
        'install': CustomInstall,
    },
    zip_safe=False,
)
