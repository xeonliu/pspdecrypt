# PSP Decrypt - Python Bindings

Easy-to-use Python library for decrypting PSP binaries and firmware files.

## Quick Start

```python
import pspdecrypt

# Decrypt a PRX file
with open('encrypted.prx', 'rb') as f:
    encrypted = f.read()

decrypted = pspdecrypt.decrypt_prx(encrypted)

with open('decrypted.elf', 'wb') as f:
    f.write(decrypted)
```

## Installation

```bash
pip install .
```

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

## Features

- ✅ Decrypt PSP PRX/executable files
- ✅ Decrypt IPL (Initial Program Loader) files
- ✅ Automatic decompression (GZIP, KL4E, KL3E, 2RLZ)
- ✅ Support for both file I/O and byte streams
- ✅ C++ implementation for performance
- ✅ Simple Python interface

## Documentation

- **[PYTHON_API.md](PYTHON_API.md)** - Complete API reference with examples
- **[INSTALL.md](INSTALL.md)** - Installation guide
- **[examples.py](examples.py)** - Usage examples

## Basic Usage

### Decrypt from file
```python
decrypted = pspdecrypt.decrypt_prx_file('game.prx')
```

### Decrypt from bytes
```python
decrypted = pspdecrypt.decrypt_prx(prx_bytes)
```

### Get file information
```python
info = pspdecrypt.get_prx_info(prx_bytes)
print(f"Tag: 0x{info['tag']:08X}")
print(f"Size: {info['elf_size']} bytes")
```

### With secure ID (for certain PRX types)
```python
secure_id = bytes.fromhex('0123456789ABCDEF0123456789ABCDEF')
decrypted = pspdecrypt.decrypt_prx(data, secure_id=secure_id)
```

## Available Functions

- `decrypt_prx(data, secure_id=None, verbose=False)` - Decrypt PRX from bytes
- `decrypt_prx_file(filename, secure_id=None, verbose=False)` - Decrypt PRX from file
- `get_prx_info(data)` - Get PRX file information
- `decrypt_ipl1(data, verbose=False)` - Decrypt IPL stage 1
- `linearize_ipl2(data)` - Linearize IPL stage 2
- `decrypt_ipl3(data)` - Decrypt IPL stage 3
- `decompress(data, max_size=-1, verbose=False)` - Decompress data

## License

GNU General Public License v3 (GPLv3)

## Credits

- Decryption code from [PPSSPP](https://github.com/hrydgard/ppsspp/)
- libkirk by draan
- KL3E & KL4E implementation by artart78
- Python bindings using [pybind11](https://github.com/pybind/pybind11)
