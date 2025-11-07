from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.install import install
import subprocess
import os
import sys


class BuildCLibraries(build_py):
    """Custom build command to compile C libraries using gcc."""
    
    def run(self):
        # Run the parent build_py first
        super().run()
        
        # Change to the project directory
        original_dir = os.getcwd()
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        try:
            # Create lib directory if it doesn't exist
            lib_dir = 'mtolib/lib'
            os.makedirs(lib_dir, exist_ok=True)
            
            # Define the compilation commands (equivalent to the Makefile)
            commands = [
                # mt_objects.so
                'gcc -shared -fPIC -include mtolib/src/main.h -o mtolib/lib/mt_objects.so mtolib/src/mt_objects.c mtolib/src/mt_heap.c mtolib/src/mt_node_test_4.c',
                # maxtree.so  
                'gcc -shared -fPIC -include mtolib/src/main.h -o mtolib/lib/maxtree.so mtolib/src/maxtree.c mtolib/src/mt_stack.c mtolib/src/mt_heap.c',
                # mt_objects_double.so
                'gcc -shared -fPIC -include mtolib/src/main_double.h -o mtolib/lib/mt_objects_double.so mtolib/src/mt_objects.c mtolib/src/mt_heap.c mtolib/src/mt_node_test_4.c',
                # maxtree_double.so
                'gcc -shared -fPIC -include mtolib/src/main_double.h -o mtolib/lib/maxtree_double.so mtolib/src/maxtree.c mtolib/src/mt_stack.c mtolib/src/mt_heap.c'
            ]
            
            # Execute each compilation command
            for cmd in commands:
                print(f"Running: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error compiling: {cmd}")
                    print(f"stdout: {result.stdout}")
                    print(f"stderr: {result.stderr}")
                    sys.exit(1)
                else:
                    print(f"Successfully compiled: {cmd.split()[-1]}")
                    
        finally:
            os.chdir(original_dir)


class InstallWithCLibraries(install):
    """Custom install command that ensures C libraries are built."""
    
    def run(self):
        # Run the build command first
        self.run_command('build_py')
        # Then run the normal install
        super().run()


setup(
    name='mtobjects',
    version='0.1.0',
    description='Max-tree based object detection and parameter extraction',
    packages=find_packages(),
    py_modules=['mto'],
    cmdclass={
        'build_py': BuildCLibraries,
        'install': InstallWithCLibraries,
    },
    package_data={'mtolib': ['lib/*.so', 'src/*.c', 'src/*.h']},
    include_package_data=True,
    install_requires=[
        'numpy',
        'astropy', 
        'Pillow',
        'scikit-image',
        'matplotlib',
    ],
    python_requires='>=3.8',
    author='Caroline Haigh',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)