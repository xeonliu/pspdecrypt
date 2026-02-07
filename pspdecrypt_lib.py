"""
PSP Decryption Library - Core functions for decrypting PSP binaries

This is a Python port of the original C++ pspdecrypt library.
"""

import struct
import zlib
import gzip
from typing import Optional, Tuple
from io import BytesIO

# Import kirk engine
from kirk_engine import (
    kirk_init,
    kirk_CMD1,
    kirk_CMD7,
    kirk_CMD11,
    KIRK_OPERATION_SUCCESS,
)

PSP_HEADER_SIZE = 0x150


def get_psp_tag(buf: bytes) -> int:
    """
    Get the PSP module tag as an unsigned int.
    
    Args:
        buf: Pointer to the ~PSP header buffer (size >= 0x150 bytes)
    
    Returns:
        PSP module tag
    """
    if len(buf) < PSP_HEADER_SIZE:
        return 0
    # Tag is at offset 0xD0
    return struct.unpack('<I', buf[0xD0:0xD4])[0]


def get_elf_size(buf: bytes) -> int:
    """
    Get the size of the decrypted & decompressed ELF module.
    
    Args:
        buf: Pointer to the ~PSP header buffer (size >= 0x150 bytes)
    
    Returns:
        The ELF data size
    """
    if len(buf) < PSP_HEADER_SIZE:
        return 0
    # elf_size is at offset 0x28
    return struct.unpack('<I', buf[0x28:0x2C])[0]


def get_psp_size(buf: bytes) -> int:
    """
    Get the size of the encrypted (possibly compressed first) ELF/PRX data + the PSP header structure.
    
    Args:
        buf: Pointer to the ~PSP header buffer (size >= 0x150 bytes)
    
    Returns:
        The PSP data size including header
    """
    if len(buf) < PSP_HEADER_SIZE:
        return 0
    # psp_size is at offset 0x2C
    return struct.unpack('<I', buf[0x2C:0x30])[0]


def get_comp_size(buf: bytes) -> int:
    """
    Get the size of the decrypted module data (possibly compressed).
    
    Args:
        buf: Pointer to the ~PSP header buffer (size >= 0x150 bytes)
    
    Returns:
        The decrypted data size
    """
    if len(buf) < PSP_HEADER_SIZE:
        return 0
    # comp_size is at offset 0xB0
    comp_size = struct.unpack('<i', buf[0xB0:0xB4])[0]
    if comp_size < 0:
        comp_size = get_psp_size(buf) - PSP_HEADER_SIZE
    return comp_size


def is_compressed(buf: bytes) -> bool:
    """
    Checks if buffer is compressed.
    
    Args:
        buf: The buffer
    
    Returns:
        True if compressed, False otherwise
    """
    if len(buf) < 4:
        return False
    
    # Check for GZIP magic
    if buf[0:2] == b'\x1f\x8b':
        return True
    
    # Check for KL4E magic
    if buf[0:4] == b'KL4E':
        return True
    
    # Check for KL3E magic  
    if buf[0:4] == b'KL3E':
        return True
    
    # Check for 2RLZ magic
    if buf[0:4] == b'2RLZ':
        return True
    
    return False


def decompress_psp(
    inbuf: bytes,
    outcapacity: int,
    verbose: bool = False
) -> Optional[bytes]:
    """
    Decompresses GZIP, KL4E, KL3E, or 2RLZ data.
    
    Args:
        inbuf: The input buffer with the compressed data
        outcapacity: The max capacity of the output buffer
        verbose: Whether to print verbose messages
    
    Returns:
        The decompressed data on success, None on error
    """
    if len(inbuf) < 4:
        return None
    
    # Check for GZIP
    if inbuf[0:2] == b'\x1f\x8b':
        try:
            return gzip.decompress(inbuf)
        except Exception as e:
            if verbose:
                print(f"GZIP decompression failed: {e}")
            return None
    
    # Check for KL4E
    if inbuf[0:4] == b'KL4E':
        try:
            from kl4e import decompress_kl4e
            return decompress_kl4e(inbuf, outcapacity, verbose)
        except Exception as e:
            if verbose:
                print(f"KL4E decompression failed: {e}")
            return None
    
    # Check for KL3E
    if inbuf[0:4] == b'KL3E':
        try:
            from kl4e import decompress_kl3e
            return decompress_kl3e(inbuf, outcapacity, verbose)
        except Exception as e:
            if verbose:
                print(f"KL3E decompression failed: {e}")
            return None
    
    # Check for 2RLZ
    if inbuf[0:4] == b'2RLZ':
        try:
            from liblzr import decompress_2rlz
            return decompress_2rlz(inbuf, outcapacity, verbose)
        except Exception as e:
            if verbose:
                print(f"2RLZ decompression failed: {e}")
            return None
    
    return None


def decrypt_prx(
    inbuf: bytes,
    size: int,
    secure_id: Optional[bytes] = None,
    verbose: bool = False
) -> Optional[bytes]:
    """
    Decrypts a PRX file.
    
    Args:
        inbuf: The input buffer
        size: Size of input buffer
        secure_id: Optional secure ID (16 bytes)
        verbose: Whether to print verbose messages
    
    Returns:
        Decrypted data on success, None on error
    """
    if len(inbuf) < PSP_HEADER_SIZE:
        if verbose:
            print("Input buffer too small for PRX header")
        return None
    
    try:
        # Import the PRX decrypter module
        from prx_decrypter import decrypt_prx_internal
        return decrypt_prx_internal(inbuf, size, secure_id, verbose)
    except Exception as e:
        if verbose:
            print(f"PRX decryption failed: {e}")
        return None


def decrypt_psar(
    inbuf: bytes,
    outdir: str,
    extract_only: bool = False,
    preipl: Optional[bytes] = None,
    verbose: bool = False,
    info_only: bool = False,
    keep_all: bool = False,
    decomp_psp: bool = True
) -> int:
    """
    Decrypts a PSAR archive.
    
    Args:
        inbuf: The input buffer
        outdir: Output directory
        extract_only: Don't decrypt files
        preipl: Optional preipl data
        verbose: Verbose output
        info_only: Only show info, don't extract
        keep_all: Keep intermediate files
        decomp_psp: Decompress PSP files
    
    Returns:
        0 on success, < 0 on error
    """
    try:
        from psar_decrypter import decrypt_psar_internal
        return decrypt_psar_internal(
            inbuf, outdir, extract_only, preipl,
            verbose, info_only, keep_all, decomp_psp
        )
    except Exception as e:
        if verbose:
            print(f"PSAR decryption failed: {e}")
        return -1


def decrypt_ipl(
    indata: bytes,
    version: int,
    filename: str,
    outdir: str,
    preipl: Optional[bytes] = None,
    verbose: bool = False,
    keep_all: bool = False
) -> int:
    """
    Decrypts an IPL file.
    
    Args:
        indata: Input data
        version: Firmware version
        filename: Base filename
        outdir: Output directory
        preipl: Optional preipl data
        verbose: Verbose output
        keep_all: Keep intermediate files
    
    Returns:
        0 on success, < 0 on error
    """
    try:
        from ipl_decrypt import decrypt_ipl_internal
        return decrypt_ipl_internal(
            indata, version, filename, outdir,
            preipl, verbose, keep_all
        )
    except Exception as e:
        if verbose:
            print(f"IPL decryption failed: {e}")
        return -1
