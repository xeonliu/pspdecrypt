# Installation Guide for PSP Decrypt Python Bindings

This guide explains how to install and use the PSP Decrypt Python library.

## Prerequisites

Before installing the Python bindings, ensure you have the following dependencies:

### System Requirements

- **Python**: Version 3.6 or higher
- **C++ Compiler**: gcc, clang, or MSVC
- **OpenSSL**: Development libraries
- **zlib**: Development libraries

### Platform-Specific Instructions

#### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install python3-dev python3-pip build-essential libssl-dev zlib1g-dev
```

#### Fedora/RHEL/CentOS

```bash
sudo dnf install python3-devel python3-pip gcc-c++ openssl-devel zlib-devel
```

#### macOS

```bash
# Install Xcode Command Line Tools if not already installed
xcode-select --install

# Install dependencies via Homebrew
brew install python openssl zlib
```

#### Windows

1. Install [Python](https://www.python.org/downloads/) (make sure to check "Add Python to PATH")
2. Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/) with C++ support
3. Install [OpenSSL](https://slproweb.com/products/Win32OpenSSL.html)

## Installation

### Option 1: Install from Source (Recommended)

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/xeonliu/pspdecrypt.git
cd pspdecrypt

# Install the package
pip install .

# Or for development (editable install)
pip install -e .
```

### Option 2: Build Without Installing

If you just want to build the module without installing it system-wide:

```bash
# Build the extension in place
python3 setup.py build

# The built module will be in build/lib.*/
# You can use it by adding this directory to your PYTHONPATH
```

## Verification

After installation, verify that the module is working:

```bash
python3 -c "import pspdecrypt; print('PSP Decrypt version:', pspdecrypt.__version__)"
```

You should see:
```
PSP Decrypt version: 1.0.0
```

## Running Tests

To run the basic tests:

```bash
# If you installed the package
python3 test_python.py

# If you only built it
PYTHONPATH=build/lib.* python3 test_python.py
```

## Trying the Examples

The `examples.py` script demonstrates various features:

```bash
# Run examples (shows usage patterns)
python3 examples.py

# Decrypt a real PSP file
python3 examples.py /path/to/your/file.prx
```

## Troubleshooting

### ImportError: No module named 'pspdecrypt'

**Solution**: Make sure you've installed the package with `pip install .` or set the PYTHONPATH correctly.

### ImportError: No module named 'pybind11'

**Solution**: Install pybind11:
```bash
pip install pybind11
```

### Compilation errors related to OpenSSL or zlib

**Solution**: Make sure the development libraries are installed. On some systems, you may need to specify the library paths:

```bash
# Ubuntu/Debian
sudo apt-get install libssl-dev zlib1g-dev

# macOS
brew install openssl zlib
export CFLAGS="-I$(brew --prefix openssl)/include -I$(brew --prefix zlib)/include"
export LDFLAGS="-L$(brew --prefix openssl)/lib -L$(brew --prefix zlib)/lib"
pip install .
```

### Windows compilation errors

**Solution**: 
1. Ensure Visual Studio Build Tools are installed with C++ support
2. Make sure OpenSSL and zlib are properly installed
3. You may need to set environment variables for include/lib paths

### Module imports but functions raise errors

**Solution**: This usually means the KIRK engine or other dependencies aren't initialized. The module should handle this automatically, but if you see issues, please report them.

## Uninstallation

To uninstall the package:

```bash
pip uninstall pspdecrypt
```

## Getting Help

If you encounter issues:

1. Check this installation guide
2. Look at the [Python API documentation](PYTHON_API.md)
3. Review the examples in `examples.py`
4. Open an issue on the GitHub repository

## Next Steps

Once installed, check out:
- [PYTHON_API.md](PYTHON_API.md) - Complete API reference
- `examples.py` - Example usage patterns
- `test_python.py` - Basic tests to verify functionality
