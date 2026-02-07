# Python Bindings Changelog

## Version 1.0.0 (2026-02-07)

### Added
- **Python bindings** for the PSP decryption library using pybind11
- **Complete API** for PRX, IPL, and data decompression
- **Dual interface**: Support for both file I/O and byte stream processing
- **Automatic decompression** of compressed PRX files
- **Error handling** with descriptive Python exceptions

### Functions Exposed
- `decrypt_prx(data, secure_id=None, verbose=False)` - Decrypt PRX from bytes
- `decrypt_prx_file(filename, secure_id=None, verbose=False)` - Decrypt PRX from file
- `get_prx_info(data)` - Get PRX file metadata
- `decrypt_ipl1(data, verbose=False)` - Decrypt IPL stage 1
- `linearize_ipl2(data)` - Linearize IPL stage 2
- `decrypt_ipl3(data)` - Decrypt IPL stage 3
- `decompress(data, max_size=-1, verbose=False)` - Decompress GZIP/KL4E/KL3E/2RLZ data

### Documentation
- **PYTHON_API.md** - Complete API reference with examples
- **INSTALL.md** - Installation guide for all platforms
- **README_PYTHON.md** - Quick start guide
- **examples.py** - Comprehensive usage examples
- **test_python.py** - Basic functionality tests

### Package Structure
- Modern Python packaging with `pyproject.toml`
- Traditional `setup.py` for backward compatibility
- `requirements.txt` for easy dependency management
- Updated `.gitignore` for Python artifacts

### Technical Details
- C++ core implementation retained for performance
- pybind11 for seamless Python-C++ interoperability
- Automatic KIRK engine initialization
- Thread-safe implementation
- Memory-efficient buffer management

### Security
- Passed CodeQL security analysis
- No unsafe const casts
- Proper memory management
- Input validation and error handling

### Supported Platforms
- Linux (tested on Ubuntu)
- macOS
- Windows (with Visual Studio Build Tools)

### Python Versions
- Python 3.6+
- Tested with Python 3.12

## Future Enhancements

Potential future additions:
- PSAR extraction and decryption from Python
- Batch processing utilities
- Progress callbacks for long operations
- Async/await support for file operations
- Pre-built wheels for common platforms
