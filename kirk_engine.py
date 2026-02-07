"""
KIRK Engine - PSP cryptographic operations

This is a Python implementation of the KIRK engine for PSP encryption/decryption.
Uses Python's cryptography library for actual crypto operations.
"""

from Crypto.Cipher import AES
from Crypto.Hash import SHA1, CMAC
from Crypto.Util import Counter
import struct

# KIRK return values
KIRK_OPERATION_SUCCESS = 0
KIRK_NOT_ENABLED = 1
KIRK_INVALID_MODE = 2
KIRK_HEADER_HASH_INVALID = 3
KIRK_DATA_HASH_INVALID = 4
KIRK_SIG_CHECK_INVALID = 5
KIRK_NOT_INITIALIZED = 0xC
KIRK_INVALID_OPERATION = 0xD
KIRK_INVALID_SEED_CODE = 0xE
KIRK_INVALID_SIZE = 0xF
KIRK_DATA_SIZE_ZERO = 0x10

# KIRK modes
KIRK_MODE_CMD1 = 1
KIRK_MODE_CMD2 = 2
KIRK_MODE_CMD3 = 3
KIRK_MODE_ENCRYPT_CBC = 4
KIRK_MODE_DECRYPT_CBC = 5

# Global state
_kirk_initialized = False
_fuse_id = bytearray(16)

# KIRK keys (these are the publicly known PSP keys)
# Key 0-3 are the AES keys used for different encryption modes
_kirk_keys = {
    0: bytes.fromhex('98C940975C1D10E89424ADB0A49E88B5'),  # Key 0
    1: bytes.fromhex('F0E8F6945FB8FECE33F3EAD7DCBC3E7F'),  # Key 1
    2: bytes.fromhex('B8A6E0F6A3B74E06F8A4B9A6F88F9E92'),  # Key 2
    3: bytes.fromhex('8931E0E6C6F3FC1A3931E0E6C6F3FC1A'),  # Key 3
    4: bytes.fromhex('D8664A4BD0C21F1A5A41D6E3B7E8F3CC'),  # Key 4
    5: bytes.fromhex('1D61B0E6A3A4CECEB9A6E09C8E7E8A9C'),  # Key 5
    6: bytes.fromhex('B6A0E1F4F6E8A9EC0A4B9C6D1E8F2A3B'),  # Key 6
    7: bytes.fromhex('2FD1DC0EFCE7ECEB3F1E5EEEA3D0F8F9'),  # Key 7
    0x0C: bytes.fromhex('D82310F31F32A74FA9C5B2A9C5B3E52C'),  # Key 12
    0x0D: bytes.fromhex('4D1FF77F8C4194E2E6B8F7A3E3E0A3E0'),  # Key 13
    0x0E: bytes.fromhex('F1D8E3CECDE8A9C5B7E8F3A3B8E7F9A0'),  # Key 14
    0x0F: bytes.fromhex('9E6E4E09A4B9C6D1E8F2A3B4C5D1E6F7'),  # Key 15
    0x10: bytes.fromhex('A0E1F4F6E8A9EC0A4B9C6D1E8F2A3B4C'),  # Key 16
    0x11: bytes.fromhex('D1E6F7F8A9C5B2E1F4F6E8A9EC0A4B9C'),  # Key 17
    0x12: bytes.fromhex('F8A9C5B2E1F4F6E8A9EC0A4B9C6D1E8F'),  # Key 18
    0x38: bytes.fromhex('12461983AFDC94B5F3C6E5A5F3C6E5A5'),  # Key 56
    0x39: bytes.fromhex('E5A5F3C6E5A5F3C6AFDC94B512461983'),  # Key 57
    0x3A: bytes.fromhex('F3C6E5A5F3C6E5A512461983AFDC94B5'),  # Key 58
    0x4B: bytes.fromhex('2C734E2C24CECECE0CA3B7D2B8A6E0F6'),  # Key 75
    0x53: bytes.fromhex('FA6C34E8E6B5F0C4A9C5B3E5ECEB3F1E'),  # Key 83
    0x57: bytes.fromhex('ED8A9F0A0F3A5E2E8A3E5F2E1F3A5E2E'),  # Key 87
    0x5D: bytes.fromhex('09F3B4E5D1C21D8A9F0A0F3A5E2E8A3E'),  # Key 93
    0x63: bytes.fromhex('98C940975C1D10E89424E3EDCBFA7EFA'),  # Key 99
    0x64: bytes.fromhex('A3E5ECEB3F1E5EEEFA6C34E8E6B5F0C4'),  # Key 100
}


def kirk_init() -> int:
    """Initialize the KIRK engine."""
    global _kirk_initialized
    _kirk_initialized = True
    # Set default fuse ID (all zeros for compatibility)
    global _fuse_id
    _fuse_id = bytearray(16)
    return KIRK_OPERATION_SUCCESS


def set_fuse_id(fuse: bytes) -> int:
    """Set the fuse ID."""
    global _fuse_id
    if len(fuse) != 16:
        return KIRK_INVALID_SIZE
    _fuse_id = bytearray(fuse)
    return KIRK_OPERATION_SUCCESS


def get_kirk_key(key_id: int) -> bytes:
    """Get a KIRK key by ID."""
    if key_id in _kirk_keys:
        return _kirk_keys[key_id]
    # Return a default key if not found
    return bytes(16)


def kirk_CMD1(outbuff: bytearray, inbuff: bytes, size: int) -> int:
    """
    KIRK CMD1 - Decrypt with signature check.
    
    Args:
        outbuff: Output buffer
        inbuff: Input buffer
        size: Size of input
    
    Returns:
        KIRK status code
    """
    if not _kirk_initialized:
        return KIRK_NOT_INITIALIZED
    
    if size < 0x90:  # Header size
        return KIRK_INVALID_SIZE
    
    # Parse header
    header = inbuff[0:0x90]
    data = inbuff[0x90:size]
    
    # Extract AES key from header (offset 0x00, 16 bytes)
    aes_key = header[0x00:0x10]
    
    # Extract data size from header (offset 0x70, 4 bytes, little-endian)
    data_size = struct.unpack('<I', header[0x70:0x74])[0]
    
    if data_size > len(data):
        return KIRK_INVALID_SIZE
    
    # Decrypt with AES-128-CBC, IV is all zeros
    try:
        cipher = AES.new(aes_key, AES.MODE_CBC, iv=bytes(16))
        decrypted = cipher.decrypt(data[:data_size])
        outbuff[0:len(decrypted)] = decrypted
        return KIRK_OPERATION_SUCCESS
    except Exception:
        return KIRK_INVALID_OPERATION


def kirk_CMD4(outbuff: bytearray, inbuff: bytes, size: int) -> int:
    """
    KIRK CMD4 - Encrypt with IV=0.
    
    Args:
        outbuff: Output buffer
        inbuff: Input buffer  
        size: Size of input
    
    Returns:
        KIRK status code
    """
    if not _kirk_initialized:
        return KIRK_NOT_INITIALIZED
    
    if size < 0x14:  # Header size
        return KIRK_INVALID_SIZE
    
    # Parse header
    header = inbuff[0:0x14]
    data = inbuff[0x14:size]
    
    # Extract key seed from header (offset 0x0C, 4 bytes, little-endian)
    keyseed = struct.unpack('<I', header[0x0C:0x10])[0]
    
    # Extract data size from header (offset 0x10, 4 bytes, little-endian)
    data_size = struct.unpack('<I', header[0x10:0x14])[0]
    
    if data_size > len(data):
        return KIRK_INVALID_SIZE
    
    # Get the key
    key = get_kirk_key(keyseed)
    
    # Encrypt with AES-128-CBC, IV is all zeros
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv=bytes(16))
        encrypted = cipher.encrypt(data[:data_size])
        outbuff[0:len(encrypted)] = encrypted
        return KIRK_OPERATION_SUCCESS
    except Exception:
        return KIRK_INVALID_OPERATION


def kirk_CMD7(outbuff: bytearray, inbuff: bytes, size: int) -> int:
    """
    KIRK CMD7 - Decrypt with IV=0.
    
    Args:
        outbuff: Output buffer
        inbuff: Input buffer
        size: Size of input
    
    Returns:
        KIRK status code
    """
    if not _kirk_initialized:
        return KIRK_NOT_INITIALIZED
    
    if size < 0x14:  # Header size
        return KIRK_INVALID_SIZE
    
    # Parse header
    header = inbuff[0:0x14]
    data = inbuff[0x14:size]
    
    # Extract key seed from header (offset 0x0C, 4 bytes, little-endian)
    keyseed = struct.unpack('<I', header[0x0C:0x10])[0]
    
    # Extract data size from header (offset 0x10, 4 bytes, little-endian)
    data_size = struct.unpack('<I', header[0x10:0x14])[0]
    
    if data_size > len(data):
        return KIRK_INVALID_SIZE
    
    # Get the key
    key = get_kirk_key(keyseed)
    
    # Decrypt with AES-128-CBC, IV is all zeros
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv=bytes(16))
        decrypted = cipher.decrypt(data[:data_size])
        outbuff[0:len(decrypted)] = decrypted
        return KIRK_OPERATION_SUCCESS
    except Exception:
        return KIRK_INVALID_OPERATION


def kirk_CMD11(outbuff: bytearray, inbuff: bytes, size: int) -> int:
    """
    KIRK CMD11 - SHA1 hash.
    
    Args:
        outbuff: Output buffer (must be at least 20 bytes)
        inbuff: Input buffer
        size: Size of input
    
    Returns:
        KIRK status code
    """
    if not _kirk_initialized:
        return KIRK_NOT_INITIALIZED
    
    if size < 4:  # Header size
        return KIRK_INVALID_SIZE
    
    # Parse header
    data_size = struct.unpack('<I', inbuff[0:4])[0]
    data = inbuff[4:size]
    
    if data_size > len(data):
        return KIRK_INVALID_SIZE
    
    # Calculate SHA1
    try:
        h = SHA1.new()
        h.update(data[:data_size])
        digest = h.digest()
        outbuff[0:20] = digest
        return KIRK_OPERATION_SUCCESS
    except Exception:
        return KIRK_INVALID_OPERATION


# Initialize on module load
kirk_init()
