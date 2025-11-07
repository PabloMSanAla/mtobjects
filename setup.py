#!/usr/bin/env python
import os
import subprocess
from pathlib import Path
from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
from setuptools.command.build import build


class CustomBuildExt(build_ext):
    """Custom build_ext command to compile C extensions (pure-Python implementation of recompile.sh)."""

    def run(self):
        print("Building C extensions...")
        project_dir = Path(__file__).parent
        mtolib_dir = project_dir / "mtolib"
        lib_dir = mtolib_dir / "lib"
        src_dir = mtolib_dir / "src"

        # Ensure lib directory exists
        lib_dir.mkdir(parents=True, exist_ok=True)

        # Remove existing shared objects to force recompilation
        for so in lib_dir.glob("*.so"):
            try:
                so.unlink()
                print(f"Removed existing {so.name}")
            except Exception as e:
                print(f"Warning: Could not remove {so.name}: {e}")

        # If sources aren't present, skip compilation with a warning
        if not src_dir.exists():
            print(f"Warning: source directory not found at {src_dir}, skipping C compilation")
        else:
            print(f"Compiling C sources from {src_dir}")
            
            # Compilation commands (run in src_dir) - using relative paths like the original recompile.sh
            cmds = [
                ["gcc", "-shared", "-fPIC", "-include", "main.h", "-o", "../lib/mt_objects.so", "mt_objects.c", "mt_heap.c", "mt_node_test_4.c"],
                ["gcc", "-shared", "-fPIC", "-include", "main.h", "-o", "../lib/maxtree.so", "maxtree.c", "mt_stack.c", "mt_heap.c"],
                ["gcc", "-shared", "-fPIC", "-include", "main_double.h", "-o", "../lib/mt_objects_double.so", "mt_objects.c", "mt_heap.c", "mt_node_test_4.c"],
                ["gcc", "-shared", "-fPIC", "-include", "main_double.h", "-o", "../lib/maxtree_double.so", "maxtree.c", "mt_stack.c", "mt_heap.c"],
            ]

            for cmd in cmds:
                try:
                    print(f"Running: {' '.join(cmd)}")
                    subprocess.check_call(cmd, cwd=str(src_dir))
                    print(f"Successfully compiled {cmd[-1].split('/')[-1]}")
                except subprocess.CalledProcessError as e:
                    print(f"Compilation failed: {' '.join(cmd)}")
                    print(f"Error: {e}")
                    raise
                except FileNotFoundError:
                    print("Error: gcc not found. Please install GCC compiler.")
                    print("On macOS: xcode-select --install")
                    print("On Ubuntu/Debian: sudo apt-get install build-essential")
                    print("On CentOS/RHEL: sudo yum groupinstall 'Development Tools'")
                    raise

        # Call parent implementation
        super().run()


class CustomBuild(build):
    """Custom build command to ensure C extensions are built"""
    
    def run(self):
        # Run build_ext before other build steps
        self.run_command('build_ext')
        super().run()


class CustomInstall(install):
    """Custom install command to ensure C extensions are built"""
    
    def run(self):
        print("Installing mtobjects with C extension compilation...")
        # Run build_ext before install to ensure compiled libraries are available
        self.run_command('build_ext')
        super().run()


# Simple setup call - configuration is in pyproject.toml
setup(
    cmdclass={
        'build': CustomBuild,
        'build_ext': CustomBuildExt,
        'install': CustomInstall,
    },
)
