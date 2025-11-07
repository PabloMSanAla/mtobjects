"""
Custom build backend that ensures C extensions are always compiled.
This wrapper around setuptools.build_meta ensures our C compilation
happens even during isolated pip builds from Git.
"""
import os
import subprocess
import sys
from pathlib import Path

# Import the standard setuptools backend
from setuptools import build_meta as _orig_backend

def _compile_c_extensions():
    """Compile C extensions - this will be called by our build backend"""
    try:
        # Get the project directory (where this file is located)
        project_dir = Path(__file__).parent
        mtolib_dir = project_dir / "mtolib"
        lib_dir = mtolib_dir / "lib" 
        src_dir = mtolib_dir / "src"

        # Check if all libraries already exist
        required_libs = ["mt_objects.so", "maxtree.so", "mt_objects_double.so", "maxtree_double.so"]
        all_libs_exist = all((lib_dir / lib).exists() for lib in required_libs)
        
        if all_libs_exist and src_dir.exists():
            # Check if any source file is newer than the oldest library
            src_files = list(src_dir.glob("*.c")) + list(src_dir.glob("*.h"))
            if src_files:
                newest_src = max(f.stat().st_mtime for f in src_files)
                oldest_lib = min((lib_dir / lib).stat().st_mtime for lib in required_libs if (lib_dir / lib).exists())
                if newest_src <= oldest_lib:
                    print("C extensions are up to date, skipping compilation")
                    return True

        print("Custom build backend: Compiling C extensions...")

        # Ensure lib directory exists
        lib_dir.mkdir(parents=True, exist_ok=True)

        # Remove existing shared objects to force recompilation
        for so in lib_dir.glob("*.so"):
            try:
                so.unlink()
                print(f"Removed existing {so.name}")
            except Exception as e:
                print(f"Warning: Could not remove {so.name}: {e}")

        # If sources aren't present, skip compilation
        if not src_dir.exists():
            print(f"Warning: source directory not found at {src_dir}, skipping C compilation")
            return False

        print(f"Compiling C sources from {src_dir}")
        
        # Compilation commands
        cmds = [
            ["gcc", "-shared", "-fPIC", "-include", "main.h", "-o", "../lib/mt_objects.so", "mt_objects.c", "mt_heap.c", "mt_node_test_4.c"],
            ["gcc", "-shared", "-fPIC", "-include", "main.h", "-o", "../lib/maxtree.so", "maxtree.c", "mt_stack.c", "mt_heap.c"],
            ["gcc", "-shared", "-fPIC", "-include", "main_double.h", "-o", "../lib/mt_objects_double.so", "mt_objects.c", "mt_heap.c", "mt_node_test_4.c"],
            ["gcc", "-shared", "-fPIC", "-include", "main_double.h", "-o", "../lib/maxtree_double.so", "maxtree.c", "mt_stack.c", "mt_heap.c"],
        ]

        for cmd in cmds:
            try:
                print(f"Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, cwd=str(src_dir), 
                                      capture_output=True, text=True, check=True)
                print(f"Successfully compiled {cmd[-1].split('/')[-1]}")
            except subprocess.CalledProcessError as e:
                print(f"Compilation failed: {' '.join(cmd)}")
                print(f"stdout: {e.stdout}")
                print(f"stderr: {e.stderr}")
                raise
            except FileNotFoundError:
                print("Error: gcc not found. Please install GCC compiler.")
                print("On macOS: xcode-select --install")
                print("On Ubuntu/Debian: sudo apt-get install build-essential")
                print("On CentOS/RHEL: sudo yum groupinstall 'Development Tools'")
                raise
        
        print("C extensions compiled successfully!")
        return True

    except Exception as e:
        print(f"Failed to compile C extensions: {e}")
        import traceback
        traceback.print_exc()
        return False


# Wrap all the standard build backend functions to ensure compilation happens

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    """Build a wheel, ensuring C extensions are compiled first"""
    print("Custom build backend: build_wheel called")
    _compile_c_extensions()
    return _orig_backend.build_wheel(wheel_directory, config_settings, metadata_directory)


def build_sdist(sdist_directory, config_settings=None):
    """Build a source distribution"""
    print("Custom build backend: build_sdist called")
    # For sdist, we don't need to compile, just ensure sources are included
    return _orig_backend.build_sdist(sdist_directory, config_settings)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    """Build an editable install, ensuring C extensions are compiled"""
    print("Custom build backend: build_editable called")
    _compile_c_extensions()
    return _orig_backend.build_editable(wheel_directory, config_settings, metadata_directory)


def get_requires_for_build_wheel(config_settings=None):
    """Get requirements for building a wheel"""
    return _orig_backend.get_requires_for_build_wheel(config_settings)


def get_requires_for_build_sdist(config_settings=None):
    """Get requirements for building sdist"""
    return _orig_backend.get_requires_for_build_sdist(config_settings)


def get_requires_for_build_editable(config_settings=None):
    """Get requirements for building editable install"""
    return _orig_backend.get_requires_for_build_editable(config_settings)


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    """Prepare metadata for wheel build"""
    print("Custom build backend: prepare_metadata_for_build_wheel called")
    _compile_c_extensions()
    return _orig_backend.prepare_metadata_for_build_wheel(metadata_directory, config_settings)


def prepare_metadata_for_build_editable(metadata_directory, config_settings=None):
    """Prepare metadata for editable build"""
    print("Custom build backend: prepare_metadata_for_build_editable called") 
    _compile_c_extensions()
    return _orig_backend.prepare_metadata_for_build_editable(metadata_directory, config_settings)


# Ensure compilation happens when this module is imported
print("Custom build backend loaded, ensuring C extensions are compiled...")
_compile_c_extensions()