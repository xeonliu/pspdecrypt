#!/usr/bin/env python3
"""
Setup script for pspdecrypt Python bindings
"""

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import os
import platform
import subprocess

class get_pybind_include(object):
    """Helper class to determine the pybind11 include path"""
    def __str__(self):
        import pybind11
        return pybind11.get_include()


# Source files for the extension
sources = [
    'pspdecrypt_python.cpp',
    'pspdecrypt_lib.cpp',
    'PrxDecrypter.cpp',
    'PsarDecrypter.cpp',
    'ipl_decrypt.cpp',
    'common.cpp',
    'syscon_ipl_keys.c',
    'libLZR.c',
    'kl4e.c',
    'libkirk/kirk_engine.c',
    'libkirk/AES.c',
    'libkirk/SHA1.c',
    'libkirk/bn.c',
    'libkirk/ec.c',
    'libkirk/amctrl.c',
]

# Platform-specific compiler flags and libraries
extra_compile_args = []
extra_link_args = []
libraries = []
include_dirs = [
    get_pybind_include(),
    '.',
    './libkirk',
]
library_dirs = []

if sys.platform == 'win32':
    # MSVC compiler flags
    extra_compile_args = ['/O2', '/std:c++14']
    
    # Try to find vcpkg installation
    vcpkg_root = os.environ.get('VCPKG_ROOT')
    if not vcpkg_root:
        # Common vcpkg installation locations
        possible_vcpkg = [
            'C:/vcpkg',
            os.path.expanduser('~/vcpkg'),
        ]
        for path in possible_vcpkg:
            if os.path.exists(path):
                vcpkg_root = path
                break
    
    if vcpkg_root:
        # Add vcpkg include and lib directories
        vcpkg_installed = os.path.join(vcpkg_root, 'installed', 'x64-windows')
        if os.path.exists(vcpkg_installed):
            include_dirs.append(os.path.join(vcpkg_installed, 'include'))
            library_dirs.append(os.path.join(vcpkg_installed, 'lib'))
    
    # Windows OpenSSL and zlib libraries (vcpkg naming)
    libraries = ['libcrypto', 'zlib']
else:
    # GCC/Clang compiler flags
    extra_compile_args = ['-O3', '-std=c++11', '-Wno-deprecated-declarations']
    # Unix-like systems
    libraries = ['z', 'crypto']

# Extension module
ext_modules = [
    Extension(
        'pspdecrypt',
        sources=sources,
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        language='c++',
    ),
]

setup(
    name='pspdecrypt',
    version='1.0.0',
    author='pspdecrypt contributors',
    description='Python bindings for PSP decryption library',
    long_description=open('README_PYTHON.md').read() if os.path.exists('README_PYTHON.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/xeonliu/pspdecrypt',
    project_urls={
        'Source': 'https://github.com/xeonliu/pspdecrypt',
        'Bug Tracker': 'https://github.com/xeonliu/pspdecrypt/issues',
    },
    ext_modules=ext_modules,
    install_requires=['pybind11>=2.6.0'],
    setup_requires=['pybind11>=2.6.0'],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: C++',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Emulators',
    ],
)
