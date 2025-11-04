#!/usr/bin/env python
import os
import subprocess
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install


class CustomBuildExt(build_ext):
    """Custom build_ext command to compile C extensions (pure-Python implementation of recompile.sh)."""

    def run(self):
        project_dir = Path(__file__).parent
        mtolib_dir = project_dir / "mtolib"
        lib_dir = mtolib_dir / "lib"
        src_dir = mtolib_dir / "src"

        # Ensure lib directory exists
        lib_dir.mkdir(parents=True, exist_ok=True)

        # Remove existing shared objects
        for so in lib_dir.glob("*.so"):
            try:
                so.unlink()
            except Exception:
                pass

        # If sources aren't present, skip compilation with a warning
        if not src_dir.exists():
            print(f"Warning: source directory not found at {src_dir}, skipping C compilation")
        else:
            # Compilation commands (run in src_dir)
            cmds = [
                ["gcc", "-shared", "-fPIC", "-include", "main.h", "-o", str(lib_dir / "mt_objects.so"), "mt_objects.c", "mt_heap.c", "mt_node_test_4.c"],
                ["gcc", "-shared", "-fPIC", "-include", "main.h", "-o", str(lib_dir / "maxtree.so"), "maxtree.c", "mt_stack.c", "mt_heap.c"],
                ["gcc", "-shared", "-fPIC", "-include", "main_double.h", "-o", str(lib_dir / "mt_objects_double.so"), "mt_objects.c", "mt_heap.c", "mt_node_test_4.c"],
                ["gcc", "-shared", "-fPIC", "-include", "main_double.h", "-o", str(lib_dir / "maxtree_double.so"), "maxtree.c", "mt_stack.c", "mt_heap.c"],
            ]

            for cmd in cmds:
                try:
                    subprocess.check_call(cmd, cwd=str(src_dir))
                except subprocess.CalledProcessError as e:
                    print(f"Compilation failed: {' '.join(cmd)}")
                    raise

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
