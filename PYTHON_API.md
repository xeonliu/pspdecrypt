# PSP Decrypt Python Bindings

Python bindings for the PSP decryption library, allowing easy decryption of PSP binaries, IPL files, and PSAR archives from Python.

## Installation

### Prerequisites

- Python 3.6 or higher
- pybind11 (will be installed automatically)
- OpenSSL development libraries (`libssl-dev` on Ubuntu/Debian)
- zlib development libraries (`zlib1g-dev` on Ubuntu/Debian)
- A C++ compiler (gcc/clang)

### Install from source

```bash
# Install dependencies (Ubuntu/Debian)
sudo apt-get install python3-dev libssl-dev zlib1g-dev

# Install the package
pip install .

# Or for development
pip install -e .
```

## Quick Start

```python
import pspdecrypt

# Decrypt a PRX file
with open('encrypted.prx', 'rb') as f:
    encrypted_data = f.read()

decrypted_data = pspdecrypt.decrypt_prx(encrypted_data)

with open('decrypted.elf', 'wb') as f:
    f.write(decrypted_data)
```

## API Reference

### PRX Decryption Functions

#### `decrypt_prx(data, secure_id=None, verbose=False)`

Decrypt a PSP PRX/executable from bytes.

**Parameters:**
- `data` (bytes): The encrypted PRX data
- `secure_id` (bytes, optional): 16-byte secure ID for PRX types 3/5/7/10
- `verbose` (bool, optional): Enable verbose output

**Returns:**
- bytes: The decrypted (and decompressed if applicable) data

**Example:**
```python
# Basic decryption
decrypted = pspdecrypt.decrypt_prx(encrypted_data)

# With secure ID
secure_id = bytes.fromhex('0123456789ABCDEF0123456789ABCDEF')
decrypted = pspdecrypt.decrypt_prx(encrypted_data, secure_id=secure_id)

# With verbose output
decrypted = pspdecrypt.decrypt_prx(encrypted_data, verbose=True)
```

#### `decrypt_prx_file(filename, secure_id=None, verbose=False)`

Decrypt a PSP PRX/executable directly from a file.

**Parameters:**
- `filename` (str): Path to the encrypted PRX file
- `secure_id` (bytes, optional): 16-byte secure ID for PRX types 3/5/7/10
- `verbose` (bool, optional): Enable verbose output

**Returns:**
- bytes: The decrypted data

**Example:**
```python
decrypted = pspdecrypt.decrypt_prx_file('game.prx')
with open('game.elf', 'wb') as f:
    f.write(decrypted)
```

#### `get_prx_info(data)`

Get information about a PRX file.

**Parameters:**
- `data` (bytes): The PRX file data (at least 0x150 bytes)

**Returns:**
- dict: A dictionary containing:
  - `tag` (int): The encryption tag value
  - `elf_size` (int): Size of the decrypted ELF
  - `psp_size` (int): Size of the encrypted data
  - `comp_size` (int): Size of compressed data
  - `is_compressed` (bool): Whether the data is compressed

**Example:**
```python
info = pspdecrypt.get_prx_info(prx_data)
print(f"Encryption tag: 0x{info['tag']:08X}")
print(f"Will decrypt to {info['elf_size']} bytes")
```

### IPL Decryption Functions

#### `decrypt_ipl1(data, verbose=False)`

Decrypt IPL stage 1.

**Parameters:**
- `data` (bytes): The encrypted IPL data
- `verbose` (bool, optional): Enable verbose output

**Returns:**
- bytes: The decrypted stage 1 data

**Example:**
```python
with open('ipl.bin', 'rb') as f:
    ipl_data = f.read()

stage1 = pspdecrypt.decrypt_ipl1(ipl_data, verbose=True)
```

#### `linearize_ipl2(data)`

Linearize IPL stage 2.

**Parameters:**
- `data` (bytes): The decrypted stage 1 data

**Returns:**
- tuple: (linearized_data, start_address)
  - `linearized_data` (bytes): The linearized data
  - `start_address` (int): The start address

**Example:**
```python
stage1 = pspdecrypt.decrypt_ipl1(ipl_data)
stage2, start_addr = pspdecrypt.linearize_ipl2(stage1)
print(f"Linearized at address: 0x{start_addr:08X}")
```

#### `decrypt_ipl3(data)`

Decrypt IPL stage 3 (only valid for firmware 1.00-2.50).

**Parameters:**
- `data` (bytes): The linearized stage 2 data

**Returns:**
- bytes: The decrypted payload

**Example:**
```python
stage1 = pspdecrypt.decrypt_ipl1(ipl_data)
stage2, _ = pspdecrypt.linearize_ipl2(stage1)
stage3 = pspdecrypt.decrypt_ipl3(stage2)
```

### Compression Functions

#### `decompress(data, max_size=-1, verbose=False)`

Decompress GZIP, KL4E, KL3E, or 2RLZ compressed data.

**Parameters:**
- `data` (bytes): The compressed data
- `max_size` (int, optional): Maximum output size (default: input_size * 10)
- `verbose` (bool, optional): Enable verbose output

**Returns:**
- bytes: The decompressed data

**Example:**
```python
decompressed = pspdecrypt.decompress(compressed_data, verbose=True)

# With size limit
decompressed = pspdecrypt.decompress(compressed_data, max_size=1024*1024)
```

## Common Use Cases

### Decrypt a game executable

```python
import pspdecrypt

# Read the encrypted EBOOT.BIN
with open('EBOOT.BIN', 'rb') as f:
    encrypted = f.read()

# Decrypt it
decrypted = pspdecrypt.decrypt_prx(encrypted, verbose=True)

# Save the decrypted ELF
with open('EBOOT.elf', 'wb') as f:
    f.write(decrypted)
```

### Process multiple files

```python
import pspdecrypt
import os
import glob

for prx_file in glob.glob('*.prx'):
    print(f"Processing {prx_file}...")
    try:
        decrypted = pspdecrypt.decrypt_prx_file(prx_file)
        output = prx_file.replace('.prx', '.elf')
        with open(output, 'wb') as f:
            f.write(decrypted)
        print(f"  ✓ Saved to {output}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
```

### Stream processing

```python
import pspdecrypt
import io

def decrypt_stream(input_stream):
    """Decrypt data from a stream"""
    data = input_stream.read()
    return io.BytesIO(pspdecrypt.decrypt_prx(data))

# Use with any file-like object
with open('encrypted.prx', 'rb') as f:
    decrypted_stream = decrypt_stream(f)
    # Process the decrypted stream
    elf_data = decrypted_stream.read()
```

### Inspect before decrypting

```python
import pspdecrypt

with open('game.prx', 'rb') as f:
    data = f.read()

# Check the file info first
info = pspdecrypt.get_prx_info(data)

if info['is_compressed']:
    print(f"File is compressed, will expand from {info['comp_size']} to {info['elf_size']} bytes")

# Now decrypt
decrypted = pspdecrypt.decrypt_prx(data)
```

## Error Handling

All functions may raise exceptions on error:

```python
import pspdecrypt

try:
    decrypted = pspdecrypt.decrypt_prx(data)
except RuntimeError as e:
    print(f"Decryption failed: {e}")
```

Common errors:
- `"Input data is too small"` - File is not a valid PRX (< 0x150 bytes)
- `"PRX decryption failed"` - Decryption failed (corrupted file or wrong secure ID)
- `"Secure ID must be exactly 16 bytes"` - Invalid secure ID provided

## Notes

- The library automatically detects and decompresses compressed PRX files
- IPL decryption is a multi-stage process (see IPL examples)
- For PSAR extraction, use the command-line tool or check `PsarDecrypter.cpp` for reference
- Secure IDs are device-specific and required only for certain PRX types (3, 5, 7, 10)

## License

This project is licensed under the GPLv3 License - see the LICENSE.TXT file for details.

## Credits

- Decryption code from [PPSSPP](https://github.com/hrydgard/ppsspp/)
- libkirk by draan
- KL3E & KL4E implementation by artart78
- Python bindings implementation using pybind11
