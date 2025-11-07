#!/usr/bin/env python3
"""
Pre-build script for mtobjects to compile C extensions
This should be run before Poetry build commands
"""
import os
import subprocess
import sys
from pathlib import Path


def main():
    """Compile C extensions before Poetry build"""
    print("Pre-build: Compiling C extensions...")
    
    # Get the project directory
    project_dir = Path(__file__).parent
    makefile_path = project_dir / "Makefile"
    
    # Try using Make first
    if makefile_path.exists():
        try:
            print("Using Makefile to compile C extensions...")
            subprocess.check_call(["make", "compile"], cwd=str(project_dir))
            print("Successfully compiled C extensions using Makefile")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Make failed, trying direct compilation...")
    
    # Fallback to direct gcc compilation
    mtolib_dir = project_dir / "mtolib"
    lib_dir = mtolib_dir / "lib"
    src_dir = mtolib_dir / "src"
    
    if not src_dir.exists():
        print(f"Warning: source directory not found at {src_dir}")
        return False
        
    # Ensure lib directory exists
    lib_dir.mkdir(parents=True, exist_ok=True)
    
    # Remove existing shared objects
    for so in lib_dir.glob("*.so"):
        try:
            so.unlink()
            print(f"Removed existing {so.name}")
        except Exception as e:
            print(f"Warning: Could not remove {so.name}: {e}")
    
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
            subprocess.check_call(cmd, cwd=str(src_dir))
            print(f"Successfully compiled {cmd[-1].split('/')[-1]}")
        except subprocess.CalledProcessError as e:
            print(f"Compilation failed: {' '.join(cmd)}")
            print(f"Error: {e}")
            return False
        except FileNotFoundError:
            print("Error: gcc not found. Please install GCC compiler.")
            print("On macOS: xcode-select --install")
            print("On Ubuntu/Debian: sudo apt-get install build-essential")
            print("On CentOS/RHEL: sudo yum groupinstall 'Development Tools'")
            return False
    
    print("All C extensions compiled successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)