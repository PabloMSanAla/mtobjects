from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import shutil
import os

# Define the C source directory
src_dir = 'mtolib/src'


class CustomBuildExt(build_ext):
    def run(self):
        # Run the normal build_ext
        super().run()
        
        # Copy the files to the expected names
        lib_dir = 'mtolib/lib'
        os.makedirs(lib_dir, exist_ok=True)
        
        # Mapping of extension names to expected file names
        extension_mapping = {
            'mtolib.lib.mt_objects': 'mt_objects.so',
            'mtolib.lib.maxtree': 'maxtree.so',
            'mtolib.lib.mt_objects_double': 'mt_objects_double.so',
            'mtolib.lib.maxtree_double': 'maxtree_double.so'
        }
        
        for ext in self.extensions:
            # Get the full path to the compiled extension
            src_path = self.get_ext_fullpath(ext.name)
            if os.path.exists(src_path):
                # Get the expected target name
                target_name = extension_mapping.get(ext.name)
                if target_name:
                    dst_path = os.path.join(lib_dir, target_name)
                    shutil.copy2(src_path, dst_path)
                    print(f"Copied {src_path} to {dst_path}")


# === Define your four C extensions ===
# This replaces your four 'gcc' commands.

# 1. Replaces: gcc ... -o ../lib/mt_objects.so ...
mt_objects_ext = Extension(
    # This is the Python path where the .so file will live
    # e.g., 'from mtolib.lib import mt_objects'
    name='mtolib.lib.mt_objects',
    
    # List of C files to compile
    sources=[
        f'{src_dir}/mt_objects.c',
        f'{src_dir}/mt_heap.c',
        f'{src_dir}/mt_node_test_4.c'
    ],
    # Directory to find .h files
    include_dirs=[src_dir],
    # Your extra gcc flags
    extra_compile_args=['-fPIC', '-include', 'main.h']
)

# 2. Replaces: gcc ... -o ../lib/maxtree.so ...
maxtree_ext = Extension(
    name='mtolib.lib.maxtree',
    sources=[
        f'{src_dir}/maxtree.c',
        f'{src_dir}/mt_stack.c',
        f'{src_dir}/mt_heap.c'
    ],
    include_dirs=[src_dir],
    extra_compile_args=['-fPIC', '-include', 'main.h']
)

# 3. Replaces: gcc ... -o ../lib/mt_objects_double.so ...
mt_objects_double_ext = Extension(
    name='mtolib.lib.mt_objects_double',
    sources=[ # Same sources as the first one
        f'{src_dir}/mt_objects.c',
        f'{src_dir}/mt_heap.c',
        f'{src_dir}/mt_node_test_4.c'
    ],
    include_dirs=[src_dir],
    # Note the different .h file
    extra_compile_args=['-fPIC', '-include', 'main_double.h']
)

# 4. Replaces: gcc ... -o ../lib/maxtree_double.so ...
maxtree_double_ext = Extension(
    name='mtolib.lib.maxtree_double',
    sources=[ # Same sources as the second one
        f'{src_dir}/maxtree.c',
        f'{src_dir}/mt_stack.c',
        f'{src_dir}/mt_heap.c'
    ],
    include_dirs=[src_dir],
    extra_compile_args=['-fPIC', '-include', 'main_double.h']
)


# === The main setup() call ===
setup(
    # This tells setuptools to build these C extensions
    ext_modules=[
        mt_objects_ext,
        maxtree_ext,
        mt_objects_double_ext,
        maxtree_double_ext
    ],
    cmdclass={'build_ext': CustomBuildExt},
    # Include packages and modules
    packages=['mtolib'],
    py_modules=['mto'],
    package_data={'mtolib': ['lib/*.so', 'src/*.c', 'src/*.h']},
    include_package_data=True,
    # Basic project info (can also be read from pyproject.toml)
    name='mtobjects',
    version='0.1.0',
    description='Max-tree based object detection and parameter extraction',
)