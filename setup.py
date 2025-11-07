#!/usr/bin/env python
import os
import subprocess
import sys
from pathlib import Path
from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
from setuptools.command.build import build
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info


def compile_c_extensions():
    """Compile C extensions using Makefile - more reliable across platforms"""
    try:
        project_dir = Path(__file__).parent
        makefile_path = project_dir / "Makefile"
        
        # Check if Makefile exists
        if not makefile_path.exists():
            print("Warning: Makefile not found, skipping C compilation")
            return False
            
        print("Building C extensions using Makefile...")
        
        # Use make to compile the C extensions
        try:
            # Try to use make to compile
            subprocess.check_call(["make", "compile"], cwd=str(project_dir))
            print("Successfully compiled C extensions using Makefile")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Make command failed or not found, trying fallback compilation...")
            
            # Fallback to direct gcc commands if make fails
            mtolib_dir = project_dir / "mtolib"
            lib_dir = mtolib_dir / "lib"
            src_dir = mtolib_dir / "src"

            # Check if all libraries already exist and are newer than source files
            required_libs = ["mt_objects.so", "maxtree.so", "mt_objects_double.so", "maxtree_double.so"]
            all_libs_exist = all((lib_dir / lib).exists() for lib in required_libs)
            
            if all_libs_exist and src_dir.exists():
                # Check if any source file is newer than the oldest library
                src_files = list(src_dir.glob("*.c")) + list(src_dir.glob("*.h"))
                if src_files:
                    newest_src = max(f.stat().st_mtime for f in src_files)
                    oldest_lib = min((lib_dir / lib).stat().st_mtime for lib in required_libs)
                    if newest_src <= oldest_lib:
                        # Libraries are up to date
                        return True

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
                return False
            else:
                print(f"Compiling C sources from {src_dir} (fallback method)")
                
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
                return True
    except Exception as e:
        print(f"Failed to compile C extensions: {e}")
        return False


class CustomBuildExt(build_ext):
    """Custom build_ext command to compile C extensions (pure-Python implementation of recompile.sh)."""

    def run(self):
        compile_c_extensions()
        # Call parent implementation
        super().run()


class CustomBuild(build):
    """Custom build command to ensure C extensions are built"""
    
    def run(self):
        # Run build_ext before other build steps
        compile_c_extensions()
        super().run()


class CustomDevelop(develop):
    """Custom develop command to ensure C extensions are built in development mode"""
    
    def run(self):
        compile_c_extensions()
        super().run()


class CustomEggInfo(egg_info):
    """Custom egg_info command to ensure C extensions are built during metadata generation"""
    
    def run(self):
        # Compile extensions when generating egg info (happens during Git installs)
        compile_c_extensions()
        super().run()


class CustomInstall(install):
    """Custom install command to ensure C extensions are built"""
    
    def run(self):
        print("Installing mtobjects with C extension compilation...")
        # Run compilation before install to ensure compiled libraries are available
        compile_c_extensions()
        super().run()


# Compile extensions immediately when setup.py is imported/executed
# This catches cases where pip might bypass our custom commands
try:
    compile_c_extensions()
except Exception as e:
    print(f"Note: Could not pre-compile C extensions: {e}")

# Simple setup call - configuration is in pyproject.toml
setup(
    cmdclass={
        'build': CustomBuild,
        'build_ext': CustomBuildExt,
        'develop': CustomDevelop,
        'egg_info': CustomEggInfo,
        'install': CustomInstall,
    },
)
