# pspdecrypt (Python Version)

A Python tool to decrypt PSP binaries and updaters (PSAR format).

This is a Python port of the original C++ pspdecrypt tool.

## Features

`pspdecrypt` is capable of decrypting `PRX` and `IPL` files as well as decrypting and extracting `PSAR` archives and its contents, including IPL stages where possible.

## Requirements

- Python 3.7 or higher
- pycryptodome library

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python pspdecrypt.py [OPTIONS] FILE
```

### General Options

- `-h, --help` - Display help and exit
- `-v, --verbose` - Enable verbose mode (mostly for debugging)
- `-i, --info` - Display information about the input file and exit
- `-c, --no-decomp` - Do not decompress GZIP/KL4E/KL3E/2RLZ decrypted data

### PSP(/PBP)-only Options

- `-o, --outfile FILE` - Output file for the decrypted binary (default: [FILE.PSP].dec)
- `-s, --secureid XSTR` - 16-bytes secure ID hex string (default: none)

### PSAR(/PBP)-only Options

- `-e, --extract-only` - Do not decrypt files contained in the PSAR

### PBP-only Options

- `-P, --psp-only` - Only extract/decrypt the .PSP executable file of the PBP
- `-A, --psar-only` - Only extract/decrypt the .PSAR updater file of the PBP

### IPL Decryption & PSAR(/PBP) Options

- `-O, --outdir DIR` - Output path for the PSAR's or IPL's contents
- `--ipl-decrypt` - Decrypt the IPL given as an argument
- `-V, --version VER` - The firmware version (eg 660) used for extracting the IPL stages
- `-p, --preipl FILE` - Preipl image used for decrypting the later IPL stages
- `-k, --keep-all` - Also keep the intermediate .gz files of later stages

## Examples

Decrypt a PSP executable:
```bash
python pspdecrypt.py game.prx
```

Extract a PSAR archive:
```bash
python pspdecrypt.py update.psar -O extracted/
```

Get info about a PBP file:
```bash
python pspdecrypt.py game.pbp --info
```

## License

Licensed under GPLv3

## Credits

- Original C++ implementation: https://github.com/xeonliu/pspdecrypt
- Decryption code from [ppsspp](https://github.com/hrydgard/ppsspp/)
- libkirk by draan
- KL3E & KL4E implementation by artart78
- PSAR extraction by artart78
- Python port by GitHub Copilot

## Note

This is a Python port with the core functionality. Some advanced features may still be in development.
The cryptographic operations use Python's pycryptodome library instead of the original libkirk C implementation.

## Migration from C++ Version

If you were using the original C++ version:

### Before (C++)
```bash
./pspdecrypt file.prx
```

### After (Python)
```bash
python pspdecrypt.py file.prx
```

The command-line options remain the same for compatibility.
