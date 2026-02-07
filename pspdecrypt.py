#!/usr/bin/env python3
"""
pspdecrypt - A tool to decrypt PSP binaries and updaters (PSAR format)

Licensed under GPLv3
Ported from C++ to Python

Decryption code originally from ppsspp (https://github.com/hrydgard/ppsspp/)
making use of libkirk by draan
"""

import argparse
import os
import struct
import sys
from pathlib import Path
from typing import Optional, Tuple

# Import our modules
from pspdecrypt_lib import (
    decrypt_prx,
    decrypt_psar,
    decrypt_ipl,
    get_psp_tag,
    get_elf_size,
    get_psp_size,
    is_compressed,
    decompress_psp,
)

# Magic numbers in Big-Endian
ELF_MAGIC = 0x7F454C46  # \x7fELF
SCE_MAGIC = 0x7E534345  # ~SCE
PSP_MAGIC = 0x7E505350  # ~PSP
PSAR_MAGIC = 0x50534152  # PSAR
PBP_MAGIC = 0x00504250  # \0PBP
PUPK_MAGIC = 0x5055504B  # PUPK

PSP_HEADER_SIZE = 0x150
MAX_PREIPL_SIZE = 0x1000


def read_magic(data: bytes, offset: int = 0) -> int:
    """Read a 32-bit magic number from data in big-endian format."""
    if len(data) < offset + 4:
        return 0
    return struct.unpack('>I', data[offset:offset+4])[0]


def check_skip_sce_header(data: bytes, offset: int = 0) -> Tuple[bytes, int]:
    """Skip SCE header if present and return modified data and offset."""
    if len(data) < offset + 8:
        return data, offset
    
    magic = read_magic(data, offset)
    if magic == SCE_MAGIC:
        # SCE header is present, get size
        size = struct.unpack('<I', data[offset+4:offset+8])[0]
        if size < 0x40:
            print(f"Error: Size in SCE header (0x{size:x}) is lower than the header!", file=sys.stderr)
            sys.exit(1)
        if offset + size > len(data):
            print(f"Error: Size in SCE header (0x{size:x}) points out of bounds!", file=sys.stderr)
            sys.exit(1)
        if len(data) - (offset + size) < 4:
            print("Error: No input data after skipping SCE header", file=sys.stderr)
            sys.exit(1)
        print(f"Skipped SCE header (0x{size:x} bytes)")
        return data, offset + size
    
    return data, offset


def get_psp_output_buffer_capacity(psp_data: bytes) -> int:
    """Get the appropriate output buffer size for a decrypted & decompressed ~PSP file."""
    elf_size = get_elf_size(psp_data)
    psp_size = get_psp_size(psp_data)
    size = max(elf_size, psp_size)
    # Align to AES block size (16 bytes)
    return (size + 15) & ~15


def decrypt_and_decompress_prx(
    in_data: bytes,
    in_size: int,
    secure_id: Optional[bytes] = None,
    verbose: bool = False,
    decomp_psp: bool = True
) -> bytes:
    """Decrypt and optionally decompress a PRX file."""
    elf_size = get_elf_size(in_data)
    
    # Decrypt the PRX
    out_data = decrypt_prx(in_data, in_size, secure_id, verbose)
    if out_data is None:
        raise ValueError("Failed to decrypt PRX")
    
    # Check if compressed and decompress if requested
    if len(out_data) >= 4 and is_compressed(out_data):
        if decomp_psp:
            try:
                decompressed = decompress_psp(out_data, elf_size, verbose)
                if decompressed:
                    if verbose:
                        print("Decompression successful")
                    return decompressed
                elif verbose:
                    print("Decompression failed")
            except Exception as e:
                if verbose:
                    print(f"Decompression failed: {e}")
        elif verbose:
            print("Skipped data decompression")
    
    return out_data


def main():
    parser = argparse.ArgumentParser(
        description="Decrypts encrypted PSP binaries (.PSP) or updaters (.PSAR). "
                    "Can also take PBP files as an input, or IPL binaries if the option is given. "
                    "Skips SCE/PUPK header for ~PSP/PBP files, if any."
    )
    
    # General options
    parser.add_argument('input_file', metavar='FILE', help='Input file to decrypt')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode (mostly for debugging)')
    parser.add_argument('-i', '--info', action='store_true', help='Display information about the input file and exit')
    parser.add_argument('-c', '--no-decomp', action='store_true', help='Do not decompress GZIP/KL4E/KL3E/2RLZ decrypted data')
    
    # PSP(/PBP)-only options
    parser.add_argument('-o', '--outfile', help='Output file for the decrypted binary (default: [FILE.PSP].dec)')
    parser.add_argument('-s', '--secureid', help='16-bytes secure ID hex string (default: none)')
    
    # PSAR(/PBP)-only options
    parser.add_argument('-e', '--extract-only', action='store_true', help='Do not decrypt files contained in the PSAR')
    
    # PBP-only options
    parser.add_argument('-P', '--psp-only', action='store_true', help='Only extract/decrypt the .PSP executable file of the PBP')
    parser.add_argument('-A', '--psar-only', action='store_true', help='Only extract/decrypt the .PSAR updater file of the PBP')
    
    # IPL decryption & PSAR(/PBP) options
    parser.add_argument('-O', '--outdir', help='Output path for the PSAR\'s or IPL\'s contents (default: [VER] if given [VER].PBP/PSAR)')
    parser.add_argument('--ipl-decrypt', action='store_true', help='Decrypt the IPL given as an argument')
    parser.add_argument('-V', '--version', type=int, help='The firmware version (eg 660) used for extracting the IPL stages')
    parser.add_argument('-p', '--preipl', help='Preipl image used for decrypting the later IPL stages')
    parser.add_argument('-k', '--keep-all', action='store_true', help='Also keep the intermediate .gz files of later stages')
    
    args = parser.parse_args()
    
    # Process input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Could not open {args.input_file}!", file=sys.stderr)
        return 1
    
    # Read input file
    with open(input_path, 'rb') as f:
        in_data = f.read()
    
    if len(in_data) < 0x30:
        print("Error: Input file is too small!", file=sys.stderr)
        return 1
    
    # Set output file if not specified
    if args.outfile is None:
        args.outfile = str(input_path) + '.dec'
    
    # Set output directory if not specified
    if args.outdir is None:
        if '.' in input_path.name:
            args.outdir = str(input_path.with_suffix(''))
        else:
            args.outdir = str(input_path) + '.extr'
    
    # Parse secure ID if provided
    secure_id = None
    if args.secureid:
        if len(args.secureid) != 32:  # 16 bytes = 32 hex chars
            print("Error: Secure ID must be 32 hex characters (16 bytes)", file=sys.stderr)
            return 1
        try:
            secure_id = bytes.fromhex(args.secureid)
        except ValueError:
            print("Error: Invalid hex string for secure ID", file=sys.stderr)
            return 1
    
    # Load preipl if specified
    preipl_data = None
    if args.preipl:
        preipl_path = Path(args.preipl)
        if not preipl_path.exists():
            print(f"Error: Could not open {args.preipl}!", file=sys.stderr)
            return 1
        with open(preipl_path, 'rb') as f:
            preipl_data = f.read()
        if len(preipl_data) > MAX_PREIPL_SIZE:
            print("Error: Preipl file too big!", file=sys.stderr)
            return 1
    
    # Handle IPL decryption
    if args.ipl_decrypt:
        if args.info:
            print("Error: No info to display for IPL...", file=sys.stderr)
            return 1
        if args.version is None:
            print("Error: You need to set --version to extract later stages of a standalone IPL.", file=sys.stderr)
            return 1
        
        try:
            decrypt_ipl(in_data, args.version, 'ipl', args.outdir, preipl_data, args.verbose, args.keep_all)
            print(f"Decrypted standalone IPL to {args.outdir}")
        except Exception as e:
            print(f"Error decrypting standalone IPL: {e}", file=sys.stderr)
            return 1
        return 0
    
    # Skip SCE header if present
    in_data, offset = check_skip_sce_header(in_data)
    
    # Handle different file types
    magic = read_magic(in_data, offset)
    
    decomp_psp = not args.no_decomp
    
    if magic == PSP_MAGIC:
        # PSP executable
        if args.info:
            tag = get_psp_tag(in_data[offset:])
            print(f"Input is an encrypted PSP executable encrypted with tag 0x{tag:08x}")
        else:
            if len(in_data) - offset < PSP_HEADER_SIZE:
                print("Error: Input file is too small!", file=sys.stderr)
                return 1
            
            try:
                out_data = decrypt_and_decompress_prx(
                    in_data[offset:],
                    get_psp_size(in_data[offset:]),
                    secure_id,
                    args.verbose,
                    decomp_psp
                )
                with open(args.outfile, 'wb') as f:
                    f.write(out_data)
                print(f"Decrypted PSP file to {args.outfile}")
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
    
    elif magic == PUPK_MAGIC:
        # PUPK-wrapped PBP
        pbp_offset = struct.unpack('<I', in_data[offset+0xc:offset+0x10])[0] + 0x18
        in_data, offset = in_data, offset + pbp_offset
        magic = read_magic(in_data, offset)
        # Fall through to PBP handling
    
    if magic == PBP_MAGIC:
        # PBP file
        handle_pbp(in_data, offset, args, secure_id, decomp_psp, preipl_data)
    
    elif magic == PSAR_MAGIC:
        # PSAR archive
        if args.info:
            print("Input is a PSAR with the following characteristics:")
        
        decrypt_psar(
            in_data[offset:],
            args.outdir,
            args.extract_only,
            preipl_data,
            args.verbose,
            args.info,
            args.keep_all,
            decomp_psp
        )
    
    elif magic == ELF_MAGIC:
        # Unencrypted ELF
        if args.info:
            print("Input is a non-encrypted PSP binary (ELF) file")
        else:
            with open(args.outfile, 'wb') as f:
                f.write(in_data[offset:])
            print(f"Non-encrypted file, copied to {args.outfile}")
    
    else:
        print("Error: Unknown input file format!", file=sys.stderr)
        return 1
    
    return 0


def handle_pbp(
    in_data: bytes,
    offset: int,
    args,
    secure_id: Optional[bytes],
    decomp_psp: bool,
    preipl_data: Optional[bytes]
):
    """Handle PBP file format."""
    # Parse PBP header
    pbp_header = in_data[offset:offset+0x28]
    if len(pbp_header) < 0x28:
        print("Error: Invalid PBP header!", file=sys.stderr)
        sys.exit(1)
    
    offsets = struct.unpack('<8I', pbp_header[8:40])
    psp_off = offsets[6]  # off_data_psp
    psar_off = offsets[7]  # off_data_psar
    
    if args.info:
        print("Input is a PBP with:")
    
    # Handle PSP executable in PBP
    if psp_off < len(in_data) - offset and not args.psar_only:
        data_offset = offset + psp_off
        _, sce_offset = check_skip_sce_header(in_data, data_offset)
        psp_magic = read_magic(in_data, sce_offset)
        
        if psp_magic == ELF_MAGIC:
            if args.info:
                print("- an unencrypted PSP (ELF) file")
            else:
                psp_end = offset + psar_off
                with open(args.outfile, 'wb') as f:
                    f.write(in_data[sce_offset:psp_end])
                print(f"Non-encrypted PSP file, writing to {args.outfile}")
        
        elif psp_magic == PSP_MAGIC:
            if args.info:
                tag = get_psp_tag(in_data[sce_offset:])
                print(f"- an encrypted PSP executable encrypted with tag 0x{tag:08x}")
            else:
                psp_size = get_psp_size(in_data[sce_offset:])
                if psp_size < PSP_HEADER_SIZE:
                    print("Error: DATA.PSP file within the input PBP is too small!", file=sys.stderr)
                    sys.exit(1)
                
                print(f"Decrypting PSP file to {args.outfile}")
                try:
                    out_data = decrypt_and_decompress_prx(
                        in_data[sce_offset:],
                        psp_size,
                        secure_id,
                        args.verbose,
                        decomp_psp
                    )
                    with open(args.outfile, 'wb') as f:
                        f.write(out_data)
                except Exception as e:
                    print(f"Error: {e}", file=sys.stderr)
                    sys.exit(1)
        
        elif args.info:
            print("- unknown DATA.PSP file data")
    
    # Handle PSAR in PBP
    if psar_off < len(in_data) - offset and not args.psp_only:
        if args.info:
            print("- a PSAR with the following characteristics:")
        else:
            print(f"Extracting PSAR to {args.outdir}")
        
        psar_data = in_data[offset + psar_off:]
        decrypt_psar(
            psar_data,
            args.outdir,
            args.extract_only,
            preipl_data,
            args.verbose,
            args.info,
            args.keep_all,
            decomp_psp
        )


if __name__ == '__main__':
    sys.exit(main())
