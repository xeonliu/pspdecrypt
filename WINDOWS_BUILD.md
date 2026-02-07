# Windows Build Support

## Overview

The pspdecrypt Python package now has full Windows support with pre-built binary wheels for Python 3.7-3.12.

## For Users

### Installation

Simply install via pip - it will automatically download the appropriate wheel for your platform:

```bash
pip install pspdecrypt
```

### Supported Platforms

- **Windows**: x64, Python 3.7-3.12
- **Linux**: manylinux x86_64, Python 3.7-3.12
- **macOS**: x86_64 and arm64, Python 3.7-3.12

## For Developers

### Building from Source on Windows

If you need to build from source (e.g., for development), you'll need:

1. **Visual Studio 2019 or later** with C++ support
2. **vcpkg** for dependencies

#### Setup vcpkg

```cmd
git clone https://github.com/microsoft/vcpkg C:\vcpkg
cd C:\vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg integrate install
```

#### Install Dependencies

```cmd
vcpkg install openssl:x64-windows zlib:x64-windows
```

#### Build the Package

```cmd
set VCPKG_ROOT=C:\vcpkg
pip install .
```

### CI/CD

The GitHub Actions workflow automatically:
1. Installs vcpkg dependencies on Windows
2. Builds wheels using cibuildwheel
3. Publishes to PyPI on releases

### Technical Details

**Compiler Flags:** `/O2 /std:c++14`

**Libraries:**
- OpenSSL (libcrypto)
- zlib

**vcpkg Integration:**
- Auto-detects vcpkg at `C:/vcpkg` or `VCPKG_ROOT`
- Automatically configures include and library paths
- Links against vcpkg-installed OpenSSL and zlib

## Troubleshooting

### Build Errors

If you encounter build errors on Windows:

1. Ensure vcpkg is installed and integrated
2. Verify OpenSSL and zlib are installed via vcpkg
3. Set `VCPKG_ROOT` environment variable if vcpkg is not at `C:\vcpkg`

### Runtime Errors

If you get DLL not found errors:
1. The wheel should bundle all necessary DLLs
2. If building from source, ensure vcpkg DLLs are in PATH or copied to the package directory

## Contributing

Improvements to Windows build support are welcome! Please test changes on:
- Windows 10/11 with MSVC 2019/2022
- Multiple Python versions (3.7-3.12)

Submit pull requests with:
- Updated build instructions
- CI workflow improvements
- Dependency management enhancements
